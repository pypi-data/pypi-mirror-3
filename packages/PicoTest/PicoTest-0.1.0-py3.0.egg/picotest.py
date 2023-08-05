# -*- coding: utf-8 -*-

###
### $Release: 0.1.0 $
### $Copyright: copyright(c) 2011 kuwata-lab.com all rights reserved $
### $License: MIT License $
###

__all__ = ('new', 'config', 'skip_when', 'todo')

import sys, os, re, time, types, traceback
sys.STDERR = sys.stderr
python2 = sys.version_info[0] == 2
python3 = sys.version_info[0] == 3

__version__ = "$Release: 0.1.0 $".split(' ')[1]
__unittest = 1
DEBUG = False
TEST = os.getenv("TEST")


class Config(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


config = Config(
    style = "verbose",    # or "plain"
    color = re.match(r'^(darwin|linux|freebsd|netbsd)', sys.platform) and
            hasattr(sys.stdout, 'isatty') and sys.stdout.isatty(),
)


_BUILDERS = []

def new():
    builder = TestBuilder()
    _BUILDERS.append(builder)
    return builder


if python2:
    def _func_argnames(func):
        func = getattr(func, '_original', func)
        return func.func_code.co_varnames[0:func.func_code.co_argcount]
    def next(g):           # python2.4 doesn't have 'next()'
        return g.next()
if python3:
    def _func_argnames(func):
        func = getattr(func, '_original', func)
        return func.__code__.co_varnames[0:func.__code__.co_argcount]

def _call_with_self(func, self):
    argnames = _func_argnames(func)
    if argnames and argnames[0] == "self":
        return func(self)
    else:
        return func()


class TestBuilder(object):

    def __init__(self):
        self._topic = TestTopic(False)

    def __call__(self, desc):
        return TestCallback(self, desc)

    def __iter__(self):
        yield self.__enter__()
        self.__exit__()

    def run(self, reporter=None, style=None):
        runner = TestRunner(reporter or _new_reporter(style))
        runner.reporter.enter_all(runner)
        try:
            runner.run_root(self._topic)
        finally:
            runner.reporter.exit_all(runner)

    def _enter_topic(self, name):
        parent = self._topic
        self._topic = TestTopic(name, parent)
        parent.add_topic(self._topic)

    def _exit_topic(self):
        self._topic = self._topic.parent

    def _add_spec(self, desc, func):
        self._topic.add_spec(desc, func)

    def before(self, func):
        self._topic.before = func

    def after(self, func):
        self._topic.after = func

    def fixture(self, gfunc):
        self._topic.fixtures[gfunc.__name__] = gfunc

    def TODO(self, desc):
        def fn():
            raise _ExpectedFailure(None)
        self._topic.add_spec(desc, fn)


class TestCallback(object):

    def __init__(self, builder, desc):
        self.builder = builder
        self.desc = desc

    def __enter__(self):
        self.builder._enter_topic(self.desc)
        return self.builder

    def __exit__(self, *args):
        self.builder._exit_topic()

    def __call__(self, func):  # for decorator
        self.builder._add_spec(self.desc, func)

    def __iter__(self):
        yield self.__enter__()
        self.__exit__()


class TestTopic(object):

    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.children = []
        self.before = None
        self.after = None
        self.fixtures = {}

    def add_topic(self, topic):
        self.children.append(topic)
        topic.parent = self

    def add_spec(self, desc, func):
        if TEST and TEST != desc: return
        self.children.append((desc, func))

    def clear(self):
        for child in self.children:
            child.parent = None
        self.children[:] = []

    def _inspect(self, depth=0):
        buf = ["  " * depth + "* " + str(self.name) + "\n"]
        for child in self.children:
            if isinstance(child, TestTopic):
                buf.append(child._inspect(depth+1))
            elif isinstance(child, tuple):
                buf.append("  " * (depth+1) + "- " + child[0] + "\n")
            else:
                assert False, "child=%r" % (child,)
        return "".join(buf)


STATUSES = ('passed', 'failed', 'error', 'skipped', 'todo')


class TestRunner(object):

    def __init__(self, reporter=None):
        self.reporter = reporter or _new_reporter()
        self._topics_stack = []
        self._topics_revstack = []
        self._exceptions = []
        self._counts = c = {}
        for k in STATUSES: c[k] = 0

    def run_root(self, root_topic):
        self.reporter.enter_file(self)
        try:
            self._run_topic(-1, root_topic, True)
        finally:
            self.reporter.exit_file(self)

    def _run_topic(self, depth, topic, root_p=False):
        self._topics_stack.append(topic)
        self._topics_revstack.insert(0, topic)
        if not root_p: self.reporter.enter_topic(depth, topic.name)
        try:
            for child in topic.children:
                #if isinstance(child, TestTopic):
                if not isinstance(child, tuple):
                    self._run_topic(depth+1, child)
                else:
                    desc, func = child
                    self._run_spec(depth+1, desc, func)
        finally:
            if not root_p: self.reporter.exit_topic(depth, topic.name)
            self._topics_stack.pop()
            self._topics_revstack.pop(0)

    def _path(self, desc):
        arr = [ topic.name for topic in self._topics_stack[1:] ]
        arr.append(desc)
        return arr

    def _run_spec(self, depth, desc, func):
        if TEST and TEST != desc: return
        self_ = unittest.TestCase('run')  # dummy argument
        self_._testMethodName = desc      # for unittest compatibility
        self.reporter.enter_spec(depth, desc)
        argnames = _func_argnames(func)
        args, generators, ex = self._run_providers(self_, argnames, desc)
        try:
            try:
                self._run_befores(self_)
                if ex:
                    raise ex
                func(*args)
                status = "passed"
            except AssertionError:
                status = "failed"
                self._exceptions.append((self._path(desc), sys.exc_info()))
            except SkipTest:
                status = "skipped"
                ex = sys.exc_info()[1]
                desc += " (reason: %s)" % (str(ex),)
            except _ExpectedFailure:
                status = "todo"
            except Exception:
                status = "error"
                self._exceptions.append((self._path(desc), sys.exc_info()))
            self._counts[status] += 1
        finally:
            try:
                self._run_afters(self_)
            finally:
                self._run_releasers(self_, generators)
            self.reporter.exit_spec(depth, desc, status)

    def _run_providers(self, self_, argnames, desc):
        args = []
        generators = []
        ex = None
        for argname in argnames:
            if argname == "self":
                arg = self_
            else:
                gfunc = self._find_fixture(argname)
                if gfunc:
                    g = _call_with_self(gfunc, self_)
                    if not isinstance(g, types.GeneratorType):
                        ex = TypeError("fixture should yield value.")
                        break
                    arg = next(g)
                    generators.append(g)
                else:
                    ex = NameError("%r: corrensponding fixture not defined." % (argname,))
                    break
            args.append(arg)
        return args, generators, ex

    def _run_releasers(self, self_, generators):
        if generators:
            for g in reversed(generators):
                try:
                    next(g)
                except StopIteration:
                    pass

    def _find_fixture(self, argname):
        for topic in self._topics_stack:
            if argname in topic.fixtures:
                return topic.fixtures[argname]

    def _run_befores(self, self_):
        for topic in self._topics_stack:
            if topic.before:
                _call_with_self(topic.before, self_)

    def _run_afters(self, self_):
        for topic in self._topics_revstack:
            if topic.after:
                _call_with_self(topic.after, self_)


class SkipTest(Exception):
    pass


class _ExpectedFailure(Exception):
    def __init__(self, exc_info=None):
        Exception.__init__(self)
        self.exc_info = exc_info


def skip_when(condition, reason):
    if condition:
        raise SkipTest(reason)


def todo(func):
    def deco(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except AssertionError:
            raise _ExpectedFailure(sys.exc_info())
        else:
            raise AssertionError("Expected to be failed (because not implemented yet), but passed unexpectedly.")
    deco._original = func
    return deco


class TestReporter(object):

    def enter_all(self, runner):
        pass

    def exit_all(self, runner):
        self.report_footer(runner._counts)

    def enter_file(self, runner):
        pass

    def exit_file(self, runner):
        self.report_exceptions(runner._exceptions)
        runner._exceptions[:] = []

    def enter_topic(self, depth, desc):
        pass

    def exit_topic(self, depth, desc):
        pass

    def enter_spec(self, depth, desc):
        pass

    def exit_spec(self, depth, desc, status):
        pass

    def report_exceptions(self, exceptions):
        sep = SEPARATOR
        if exceptions:
            print(sep)
            for path, exc_info in exceptions:
                self._report_exception(path, exc_info)
                print(sep)

    def _report_exception(self, path, exc_info):
        ex = exc_info[1]
        if isinstance(ex, AssertionError):
            print("[%s] %s" % (color.failed("Failed"), " > ".join(path)))
        else:
            print("[%s] %s" % (color.error("ERROR"), " > ".join(path)))
        pattern = self._pattern
        for s in traceback.format_exception(*exc_info)[1:]:
            if DEBUG or not s.startswith(pattern):
                sys.stdout.write(s)

    _pattern = '  File "%s", line ' % (re.sub(r'\.py[co]?$', '.py', __file__))

    def report_footer(self, counts):
        total = sum([ counts[st] for st in STATUSES ])
        buf = []; add = buf.append
        add("## total:%s" % total)
        for st in STATUSES:
            s = "%s:%s" % (st, counts[st])
            if counts[st]: s = color.status(st, s)
            add(", " + s)
        print("".join(buf))

    def report_filename(self, filename):
        print(filename)


SEPARATOR = "----------------------------------------------------------------------"


class VerboseReporter(TestReporter):

    _labels = { "passed": "passed", "failed": "Failed", "error": "ERROR", "skipped": "Skipped", "todo": "TODO" }

    def enter_topic(self, depth, desc):
        print("%s* %s" % ("  " * depth, color.topic((desc)), ))

    def exit_spec(self, depth, desc, status):
        print("%s- [%s] %s" % ("  " * depth, color.status(status, self._labels[status]), color.spec(desc), ))

    def report_filename(self, filename):
        print("#### " + filename)


class SimpleReporter(TestReporter):
    _superclass = TestReporter

    _labels = { "passed": ".", "failed": "f", "error": "E", "skipped": "s", "todo": "t" }

    def exit_spec(self, depth, desc, status):
        sys.stdout.write(color.status(status, self._labels[status]))
        sys.stdout.flush()

    def report_exceptions(self, exceptions):
        sys.stdout.write("\n")
        self._superclass.report_exceptions(self, exceptions)

    def report_filename(self, filename):
        sys.stdout.write(filename + ": ")


class PlainReporter(TestReporter):
    _superclass = TestReporter

    _labels = { "passed": ".", "failed": "f", "error": "E", "skipped": "s", "todo": "t" }
    _newline = ""

    def exit_spec(self, depth, desc, status):
        sys.stdout.write(color.status(status, self._labels[status]))
        sys.stdout.flush()

    def report_exceptions(self, exceptions):
        if exceptions:
            sys.stdout.write("\n")
            self._newline = ""
        else:
            self._newline = "\n"
        self._superclass.report_exceptions(self, exceptions)

    def report_filename(self, filename):
        pass

    def report_footer(self, counts):
        sys.stdout.write(self._newline)
        self._superclass.report_footer(self, counts)


_reporter_classes = {
    'verbose': VerboseReporter,   'v': VerboseReporter,
    'simple':  SimpleReporter,    's': SimpleReporter,
    'plain':   PlainReporter,     'p': PlainReporter,
}

def _new_reporter(style=None, error=True):
    if not style:
        style = os.getenv('STYLE') or config.style
    klass = _reporter_classes.get(style)
    if klass:
        return klass()
    elif error:
        raise ValueError("%r: unknown style name ('verbose', 'simple', or 'plain' available)." % (style,))
    else:
        return None


class Color(object):

    def normal (self, s):  return s
    def bold   (self, s):  return config.color and "\x1b[0;1m%s\x1b[22m" % s or s
    def black  (self, s):  return config.color and "\x1b[1;30m%s\x1b[0m" % s or s
    def red    (self, s):  return config.color and "\x1b[1;31m%s\x1b[0m" % s or s
    def green  (self, s):  return config.color and "\x1b[1;32m%s\x1b[0m" % s or s
    def yellow (self, s):  return config.color and "\x1b[1;33m%s\x1b[0m" % s or s
    def blue   (self, s):  return config.color and "\x1b[1;34m%s\x1b[0m" % s or s
    def magenta(self, s):  return config.color and "\x1b[1;35m%s\x1b[0m" % s or s
    def cyan   (self, s):  return config.color and "\x1b[1;36m%s\x1b[0m" % s or s
    def white  (self, s):  return config.color and "\x1b[1;37m%s\x1b[0m" % s or s


color = Color()
color.topic   = color.bold
color.spec    = color.normal
color.passed  = color.green
color.failed  = color.red
color.error   = color.red
color.skipped = color.yellow
color.todo    = color.yellow
color.status  = lambda status, s: getattr(color, status)(s)


##
## unittest support
##

try:
    import unittest2 as unittest
    from unittest2 import SkipTest
    from unittest2.case import _ExpectedFailure
except ImportError:
    if python2: sys.exc_clear()
    import unittest
    try:
        from unittest import SkipTest
        from unittest.case import _ExpectedFailure
    except ImportError:
        if python2: sys.exc_clear()

def assertTextEqual(self, text1, text2):
    import difflib
    msg = ""
    if text1 != text2:
        lines1 = text1.splitlines(True)
        lines2 = text2.splitlines(True)
        lst = [d for d in difflib.unified_diff(lines1, lines2, "expected", "actual")]
        msg = "texts are not equal.\n" + ''.join(lst)
    assert text1 == text2, msg

unittest.TestCase.assertTextEqual = assertTextEqual
del assertTextEqual


##
## main
##
def main(*args):
    sys_argv = sys.argv[:]
    sys_argv[1:1] = args
    n_errors = MainApp(sys_argv).run()
    sys.exit(n_errors)


class MainApp(object):

    def __init__(self, sys_argv=None):
        if sys_argv is None: sys_argv = sys.argv
        self.sys_argv = sys_argv
        self.style = self.sys_argv[0] == __file__ and "plain" or "verbose"
        self.command = "picotest.py"

    def run(self, args=None):
        if args is None: args = self.sys_argv[1:]
        parser = self._new_parser()
        opts, args = parser.parse_args(args)
        ## help or version
        if opts.help:
            sys.stdout.write(self._help_message(parser))
            return 0
        if opts.version:
            sys.stdout.write(self._version_info())
            return 0
        ## import picotest
        import picotest
        picotest.SkipTest = SkipTest
        picotest._ExpectedFailure = _ExpectedFailure
        ## debug
        global DEBUG
        if opts.debug:
            DEBUG = True
            picotest.DEBUG = True
        ## test name
        global TEST
        if opts.test:
            TEST = opts.test
        ## reporting style
        style = opts.style or self.style
        reporter = _new_reporter(style, False)
        if not reporter:
            parser.error("-s %s: unknown style (expected: verbose/simple/plain, or v/s/p)" % (opts.style,))
        ## file existence
        for fpath in args:
            if not os.path.exists(fpath):
                parser.error("%s: file or directory not found." % (fpath,))
        ## run tests
        runner = TestRunner(reporter)
        reporter.enter_all(runner)
        self._run_tests(args, reporter, runner)
        reporter.exit_all(runner)
        ## return number of failed and error tests
        counts = runner._counts
        return counts['failed'] + counts['error']

    def _run_tests(self, filepaths, reporter, runner):
        def run_builders(builders, fpath):
            reporter.report_filename(fpath)
            for b in builders:
                runner.run_root(b._topic)
            builders[:] = []
        ## for sys.argv[0]
        if self.sys_argv[0] != __file__:
            run_builders(_BUILDERS, self.sys_argv[0])
        ## for sys.argv[1:]
        import picotest     # important! dont' remove!
        for fpath in filepaths:
            self._load_file_or_dir(fpath, run_builders)

    def _load_file_or_dir(self, fpath, run_builders):
        import glob, picotest
        if os.path.isfile(fpath):
            _load_file(fpath)
            run_builders(picotest._BUILDERS, fpath)
        elif os.path.isdir(fpath):
            for child in glob.glob(fpath + "/*"):
                self._load_file_or_dir(child, run_builders)
        else:
            raise ValueError("%s: neighter file nor directory." % (fpath,))

    def _new_parser(self):
        import optparse
        parser = optparse.OptionParser(conflict_handler="resolve")
        parser.add_option("-h", "--help",       action="store_true",     help="show help")
        parser.add_option("-v", dest="version", action="store_true",     help="verion of picotest.py")
        parser.add_option("-s", dest="style",   metavar="STYLE",         help="reporting style (plain/simple/verbose, or p/s/v)")
        parser.add_option("-D", dest="debug",   action="store_true",     help="print full backtrace when failed or error")
        parser.add_option(      "--test",       metavar="NAME",          help="specify test name to do")
        return parser

    def _help_message(self, parser):
        msg = parser.format_help()
        msg = re.sub(r'^.*\n.*\n[oO]ptions:\n', '', msg)
        return "Usage: python -m picotest [options] [file or directory...]\n" + msg

    def _version_info(self):
        return __version__ + "\n"


def _load_file(filepath):
    mod_name = re.sub(r'\.py[co]?$', '', os.path.basename(filepath))
    vars = {'__file__': filepath, '__name__': mod_name}
    f = open(filepath); content = f.read(); f.close()
    code = compile(content, filepath, "exec")
    exec(code, vars, vars)


if __name__ == '__main__':
    main()
