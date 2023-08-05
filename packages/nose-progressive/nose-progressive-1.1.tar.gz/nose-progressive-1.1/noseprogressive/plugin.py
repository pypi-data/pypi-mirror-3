from functools import partial
from os import getcwd
import pdb
import sys

from nose.plugins import Plugin

from noseprogressive.runner import ProgressiveRunner
from noseprogressive.wrapping import cmdloop, set_trace, StreamWrapper


class ProgressivePlugin(Plugin):
    """A nose plugin which has a progress bar and formats tracebacks for humans"""
    name = 'progressive'
    _totalTests = 0
    score = 10000  # Grab stdout and stderr before the capture plugin.

    def __init__(self, *args, **kwargs):
        super(ProgressivePlugin, self).__init__(*args, **kwargs)
        # Same wrapping pattern as the built-in capture plugin. The lists
        # shouldn't be necessary, but they don't cost much, and I have to
        # wonder why capture uses them.
        self._stderr, self._stdout, self._set_trace, self._cmdloop = \
            [], [], [], []

    def begin(self):
        """Make some monkeypatches to dodge progress bar.

        Wrap stderr and stdout to keep other users of them from smearing the
        progress bar. Wrap some pdb routines to stop showing the bar while in
        the debugger.

        """
        # The calls to begin/finalize end up like this: a call to begin() on
        # instance A of the plugin, then a paired begin/finalize for each test
        # on instance B, then a final call to finalize() on instance A.

        # TODO: Do only if isatty.
        self._stderr.append(sys.stderr)
        sys.stderr = StreamWrapper(sys.stderr, self)  # TODO: Any point?

        self._stdout.append(sys.stdout)
        sys.stdout = StreamWrapper(sys.stdout, self)

        self._set_trace.append(pdb.set_trace)
        pdb.set_trace = set_trace

        self._cmdloop.append(pdb.Pdb.cmdloop)
        pdb.Pdb.cmdloop = cmdloop

        # nosetests changes directories to the tests dir when run from a
        # distribution dir, so save the original cwd for relativizing paths.
        self._cwd = '' if self.conf.options.absolute_paths else getcwd()

    def finalize(self, result):
        """Put monkeypatches back as we found them."""
        sys.stderr = self._stderr.pop()
        sys.stdout = self._stdout.pop()
        pdb.set_trace = self._set_trace.pop()
        pdb.Pdb.cmdloop = self._cmdloop.pop()

    def options(self, parser, env):
        super(ProgressivePlugin, self).options(parser, env)
        parser.add_option('--progressive-function-color',
                          type='int',
                          dest='function_color',
                          default=env.get('NOSE_PROGRESSIVE_FUNCTION_COLOR', 12),
                          help='Color of function names in tracebacks. An '
                               'ANSI color expressed as a number 0-15.')
        parser.add_option('--progressive-dim-color',
                          type='int',
                          dest='dim_color',
                          default=env.get('NOSE_PROGRESSIVE_DIM_COLOR', 8),
                          help='Color of de-emphasized text (like editor '
                               'shortcuts) in tracebacks. An ANSI color '
                               'expressed as a number 0-15.')
        parser.add_option('--progressive-advisories',
                          action='store_true',
                          dest='show_advisories',
                          default=env.get('NOSE_PROGRESSIVE_ADVISORIES', False),
                          help='Show skips and deprecation exceptions in '
                               'addition to failures and errors.')
        parser.add_option('--progressive-abs',
                          action='store_true',
                          dest='absolute_paths',
                          default=env.get('NOSE_PROGRESSIVE_ABSOLUTE_PATHS', False),
                          help='Display paths in traceback as absolute, '
                               'rather than relative to the current working '
                               'directory.')
        parser.add_option('--progressive-editor',
                          type='string',
                          action='store',
                          dest='editor',
                          default=env.get('NOSE_PROGRESSIVE_EDITOR',
                                          env.get('EDITOR', 'vi')),
                          help='The editor to use for the shortcuts in '
                               'tracebacks. Defaults to the value of $EDITOR '
                               'and then "vi".')

    def prepareTestLoader(self, loader):
        """Insert ourselves into loader calls to count tests.

        The top-level loader call often returns lazy results, like a LazySuite.
        This is a problem, as we would destroy the suite by iterating over it
        to count the tests. Consequently, we monkeypatch the top-level loader
        call to do the load twice: once for the actual test running and again
        to yield something we can iterate over to do the count.

        """
        def capture_suite(orig_method, *args, **kwargs):
            """Intercept calls to the loader before they get lazy.

            Re-execute them to grab a copy of the possibly lazy suite, and
            count the tests therein.

            """
            self._totalTests += orig_method(*args, **kwargs).countTestCases()
            return orig_method(*args, **kwargs)

        # TODO: If there's ever a practical need, also patch loader.suiteClass
        # or even TestProgram.createTests. createTests seems to be main top-
        # level caller of loader methods, and nose.core.collector() (which
        # isn't even called in nose) is an alternate one.
        if hasattr(loader, 'loadTestsFromNames'):
            loader.loadTestsFromNames = partial(capture_suite,
                                                loader.loadTestsFromNames)
        return loader

    def prepareTestRunner(self, runner):
        """Replace TextTestRunner with something that prints fewer dots."""
        return ProgressiveRunner(self._cwd,
                                 self._totalTests,
                                 runner.stream,
                                 verbosity=self.conf.verbosity,
                                 config=self.conf)  # So we don't get a default
                                                    # NoPlugins manager

    def prepareTestResult(self, result):
        """Hang onto the progress bar so the StreamWrappers can grab it."""
        self.bar = result.bar
