# -*- coding: utf-8 -*-

###
### $Release: 0.1.0 $
### $Copyright: copyright(c) 2011 kuwata-lab.com all rights reserved $
### $License: MIT License $
###

import sys, os, re, shutil
sys.STDERR = sys.stderr
python2 = sys.version_info[0] == 2
python3 = sys.version_info[0] == 3
python24 = python2 and sys.version_info[1] <= 4
python31 = python3 and sys.version_info[1] <= 1
with_statement_not_available = python24

try:
    import unittest2 as unittest
except ImportError:
    if python2: sys.exc_clear()
    import unittest

from subprocess import Popen, PIPE, STDOUT

def _run(command):
    p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()  # or p.communicate("input string")
    status_code = p.returncode
    return out, err, status_code

def _run_picotest(input, encoding):
    filename = "_test_pico.py"
    try:
        f = open(filename, "w"); f.write(input); f.close()
        command = "%s %s" % (sys.executable, filename)
        out, err, status_code = _run(command)
        if python3:
            out = out.decode(encoding)
            err = err.decode(encoding)
        return out, err, status_code
    finally:
        os.unlink(filename)

def _convert_with_statement_into_for_statement(input):
    input = re.sub(r'with (.*) as (.*):', r'for \2 in \1:', input)
    input = re.sub(r'with (.*):',         r'for _ in \1:',  input)
    input = re.sub(r'(from __future__ import with_statement)',  r'#\1',  input)
    return input


def colorize(text):
    text = text.replace("<b>",  "\x1b[0;1m")
    text = text.replace("</b>", "\x1b[22m")
    text = text.replace("<R>",  "\x1b[1;31m")
    text = text.replace("</R>", "\x1b[0m")
    text = text.replace("<G>",  "\x1b[1;32m")
    text = text.replace("</G>", "\x1b[0m")
    text = text.replace("<Y>",  "\x1b[1;33m")
    text = text.replace("</Y>", "\x1b[0m")
    return text

def monolize(text):
    return re.sub(r'</?[bRGY]>', "", text)

import picotest


class TestReporter_TC(unittest.TestCase):

    INPUT = r"""
from __future__ import with_statement
import picotest
from picotest import skip_when, todo
picotest.config.color = %(COLOR)s
test = picotest.new()

with test("ClassName"):

  with test("#method1()"):

    @test("1+1 should be 2")  # passed
    def _():
      assert 1+1 == 2

    @test("1-1 should be 0")  # failed
    def _():
      assert 1-1 == 2

    @test("1/1 should be infinite")  # error
    def _():
      #assert 1/1 == 1
      foobarbaz

    @test("1*1 should be 1")  # skipped
    def _():
      skip_when(1*1 == 0, "REASON1") # not skipped
      skip_when(1*1 == 1, "REASON2") # skipped
      x = 1/0

    @test("1**1 should be 1")  # todo
    @todo
    def _():
      assert 1**1 == 2   # expected failure

    @test("1**1 should not be 0")  # todo
    @todo
    def _():
      assert 1**1 == 1   # unexpected success

  with test("#method2()"):

    with test("when base is not specified"):
      @test("int('11') should be 11")
      def _():
        assert int('11') == 11

    with test("when base is 8"):
      @test("int('11', 8) should be 9")
      def _():
        assert int('11', 8) == 9

if __name__ == "__main__":
  test.run(style="%(STYLE)s")
"""[1:]

    EXPECTED_ERROR = r"""
----------------------------------------------------------------------
[<R>Failed</R>] ClassName > #method1() > 1-1 should be 0
  File "_test_pico.py", line 17, in _
    assert 1-1 == 2
AssertionError
----------------------------------------------------------------------
[<R>ERROR</R>] ClassName > #method1() > 1/1 should be infinite
  File "_test_pico.py", line 22, in _
    foobarbaz
NameError: global name 'foobarbaz' is not defined
----------------------------------------------------------------------
[<R>Failed</R>] ClassName > #method1() > 1**1 should not be 0
AssertionError: Expected to be failed (because not implemented yet), but passed unexpectedly.
----------------------------------------------------------------------
"""[1:]

    EXPECTED_FOOTER = r"""
## total:8, <G>passed:3</G>, <R>failed:2</R>, <R>error:1</R>, <Y>skipped:1</Y>, <Y>todo:1</Y>
"""[1:]

    EXPECTED_VERBOSE = r"""
* <b>ClassName</b>
  * <b>#method1()</b>
    - [<G>passed</G>] 1+1 should be 2
    - [<R>Failed</R>] 1-1 should be 0
    - [<R>ERROR</R>] 1/1 should be infinite
    - [<Y>Skipped</Y>] 1*1 should be 1 (reason: REASON2)
    - [<Y>TODO</Y>] 1**1 should be 1
    - [<R>Failed</R>] 1**1 should not be 0
  * <b>#method2()</b>
    * <b>when base is not specified</b>
      - [<G>passed</G>] int('11') should be 11
    * <b>when base is 8</b>
      - [<G>passed</G>] int('11', 8) should be 9
"""[1:] + EXPECTED_ERROR + EXPECTED_FOOTER

    EXPECTED_SIMPLE = r"""
<G>.</G><R>f</R><R>E</R><Y>s</Y><Y>t</Y><R>f</R><G>.</G><G>.</G>
"""[1:] + EXPECTED_ERROR + EXPECTED_FOOTER

    EXPECTED_PLAIN = r"""
<G>.</G><R>f</R><R>E</R><Y>s</Y><Y>t</Y><R>f</R><G>.</G><G>.</G>
"""[1:] + EXPECTED_ERROR + EXPECTED_FOOTER

    def _do_test(self, input, expected, encoding='utf-8'):
        if with_statement_not_available:
            input = _convert_with_statement_into_for_statement(input)
        out, err, status_code = _run_picotest(input, encoding)
        self.assertTextEqual("", err)
        self.assertTextEqual(expected, out)

    def test_verbose_style_in_mono(self):
        input = self.INPUT % {'STYLE': "verbose", 'COLOR': False}
        expected = monolize(self.EXPECTED_VERBOSE)
        self._do_test(input, expected)

    def test_verbose_style_in_color(self):
        input = self.INPUT % {'STYLE': "verbose", 'COLOR': True}
        expected = colorize(self.EXPECTED_VERBOSE)
        self._do_test(input, expected)

    def test_verbose_style_with_main(self):
        input = self.INPUT % {'STYLE': "verbose", 'COLOR': True}
        input = re.sub(r'(if __name__ == "__main__":\n)(.|\n)*',
                       '\\1    picotest.main("-s", "verbose")\n', input)
        expected = "#### _test_pico.py\n" + colorize(self.EXPECTED_VERBOSE)
        self._do_test(input, expected)

    def test_simple_style_in_mono(self):
        input = self.INPUT % {'STYLE': "simple", 'COLOR': False}
        expected = monolize(self.EXPECTED_SIMPLE)
        self._do_test(input, expected)

    def test_simple_style_in_color(self):
        input = self.INPUT % {'STYLE': "simple", 'COLOR': True}
        expected = colorize(self.EXPECTED_SIMPLE)
        self._do_test(input, expected)

    def test_simple_style_with_main(self):
        input = self.INPUT % {'STYLE': "simple", 'COLOR': True}
        input = re.sub(r'(if __name__ == "__main__":\n)(.|\n)*',
                       '\\1    picotest.main("-s", "simple")\n', input)
        expected = "_test_pico.py: " + colorize(self.EXPECTED_SIMPLE)
        self._do_test(input, expected)

    def test_plain_style_in_mono(self):
        input = self.INPUT % {'STYLE': "plain", 'COLOR': False}
        expected = monolize(self.EXPECTED_PLAIN)
        self._do_test(input, expected)

    def test_plain_style_in_color(self):
        input = self.INPUT % {'STYLE': "plain", 'COLOR': True}
        expected = colorize(self.EXPECTED_PLAIN)
        self._do_test(input, expected)

    def test_plain_style_with_main(self):
        input = self.INPUT % {'STYLE': "plain", 'COLOR': True}
        input = re.sub(r'(if __name__ == "__main__":\n)(.|\n)*',
                       '\\1    picotest.main("-s", "plain")\n', input)
        expected = colorize(self.EXPECTED_PLAIN)
        self._do_test(input, expected)


class TestRunner_TC(unittest.TestCase):

    def _do_test(self, input, expected, encoding='utf-8'):
        if with_statement_not_available:
            input = _convert_with_statement_into_for_statement(input)
        out, err, status_code = _run_picotest(input, encoding)
        self.assertTextEqual("", err)
        self.assertTextEqual(expected, out)

    def test_fiters_by_TEST_environment(self):
        input = r"""
from __future__ import with_statement
import picotest
test = picotest.new()

with test("ClassName1"):
  with test("#method1()"):
    @test("1+1==2")
    def _():
      assert 1+1 == 2
    @test("1-1==0")
    def _():
      assert 1-1 == 0
  with test("#method2()"):
    @test("1*1==1")
    def _():
      assert 1*1 == 1
    @test("1/1==1")
    def _():
      assert 1/1 == 1

if __name__ == "__main__":
  test.run()
"""[1:]
        expected = r"""
* ClassName1
  * #method1()
  * #method2()
    - [passed] 1*1==1
## total:1, passed:1, failed:0, error:0, skipped:0, todo:0
"""[1:]
        try:
            bkup = os.getenv('TEST', None)
            os.environ['TEST'] = '1*1==1'
            self._do_test(input, expected)
        finally:
            del os.environ['TEST']
            if bkup: os.environ['TEST'] = bkup

    def test_before_and_after_fixtures_are_called_for_each_test(self):
        input = r"""
from __future__ import with_statement
import picotest
test = picotest.new()

@test.before
def _():
  print("!!! All: before() called")
@test.after
def _():
  print("!!! All: after() called")

with test("Parent"):
  @test.before
  def _(self):
    self.team = "SOS"
    print("!!!   Parent: before() called")
  @test.after
  def _(self):
    assert self.team == "SOS"
    print("!!!   Parent: after() called")
  #
  with test("Child"):
    @test.before
    def _(self):
      self.name = "Sasaki"
      print("!!!     Child: before() called")
    @test.after
    def _(self):
      assert self.name == "Sasaki"
      print("!!!     Child: after() called")
    #
    @test("test#1")
    def _(self):
      assert self.name == "Sasaki"
      assert self.team == "SOS"
      print("!!! desc=%r" % self._testMethodName)
    #
    @test("test#2")
    def _(self):
      assert self.name == "Sasaki"
      assert self.team == "SOS"
      print("!!! desc=%r" % self._testMethodName)

if __name__ == "__main__":
  test.run()
"""[1:]
        expected = r"""
* Parent
  * Child
!!! All: before() called
!!!   Parent: before() called
!!!     Child: before() called
!!! desc='test#1'
!!!     Child: after() called
!!!   Parent: after() called
!!! All: after() called
    - [passed] test#1
!!! All: before() called
!!!   Parent: before() called
!!!     Child: before() called
!!! desc='test#2'
!!!     Child: after() called
!!!   Parent: after() called
!!! All: after() called
    - [passed] test#2
## total:2, passed:2, failed:0, error:0, skipped:0, todo:0
"""[1:]
        self._do_test(input, expected)

    def test_after_fixtures_are_called_even_when_error_raised(self):
        input = r"""
from __future__ import with_statement
import picotest
test = picotest.new()

with test("Parent"):
  @test.before
  def _(self):  print("!!! Parent: before() called")
  @test.after
  def _(self):  print("!!! Parent: after() called")
  #
  with test("Child"):
    @test.before
    def _(self):  print("!!!   Child: before() called")
    @test.after
    def _(self):  print("!!!   Child: after() called")
    #
    @test("test#1")
    def _(self):  assert 1+1 == 0
    #
    @test("test#2")
    def _(self):  raise ValueError("failed")

if __name__ == "__main__":
  test.run()
"""[1:]
        expected = r"""
* Parent
  * Child
!!! Parent: before() called
!!!   Child: before() called
!!!   Child: after() called
!!! Parent: after() called
    - [Failed] test#1
!!! Parent: before() called
!!!   Child: before() called
!!!   Child: after() called
!!! Parent: after() called
    - [ERROR] test#2
----------------------------------------------------------------------
[Failed] Parent > Child > test#1
  File "_test_pico.py", line 18, in _
    def _(self):  assert 1+1 == 0
AssertionError
----------------------------------------------------------------------
[ERROR] Parent > Child > test#2
  File "_test_pico.py", line 21, in _
    def _(self):  raise ValueError("failed")
ValueError: failed
----------------------------------------------------------------------
## total:2, passed:0, failed:1, error:1, skipped:0, todo:0
"""[1:]
        self._do_test(input, expected)

    def test_raises_NameError_when_fixture_not_found(self):
        input = r"""
from __future__ import with_statement
import picotest
test = picotest.new()

@test.fixture
def sasaki():
  yield "Sasaki"
#
with test("Example"):
  @test("when fixture not found")
  def _(sasaki, haruhi):
    pass
#
if __name__ == "__main__":
  test.run()
"""[1:]
        expected = r"""
* Example
  - [ERROR] when fixture not found
----------------------------------------------------------------------
[ERROR] Example > when fixture not found
NameError: 'haruhi': corrensponding fixture not defined.
----------------------------------------------------------------------
## total:1, passed:0, failed:0, error:1, skipped:0, todo:0
"""[1:]
        self._do_test(input, expected)

    def test_fixture_decorator_defines_generator_based_fixture(self):
        input = r"""
from __future__ import with_statement
import picotest
test = picotest.new()

@test.fixture
def TITLE(self):
  print("# setup TITLE")
  self._TITLE = "The Melancholy of HARUHI SUZUMIYA"
  yield self._TITLE
  print("# teardown TITLE")

with test("ClassName"):
  with test("#method1()"):
    @test.fixture
    def member():
      print("# setup member")
      yield "Haruhi"
      print("# teardown member")
    #
    @test.fixture
    def team(self):
      print("# setup team")
      self._team = "SOS"
      yield "SOS"
      print("# teardown team")
    #
    @test("member should be provided")
    def _(self, member, team, TITLE):
      print("# TITLE = %r" % (TITLE, ))
      assert self._TITLE == TITLE
      print("# member = %r, team = %r" % (member, team))
      assert member == "Haruhi"
      assert team == "SOS"
      assert self._team == team

if __name__ == "__main__":
  test.run()
"""[1:]
        expected = r"""
* ClassName
  * #method1()
# setup member
# setup team
# setup TITLE
# TITLE = 'The Melancholy of HARUHI SUZUMIYA'
# member = 'Haruhi', team = 'SOS'
# teardown TITLE
# teardown team
# teardown member
    - [passed] member should be provided
## total:1, passed:1, failed:0, error:0, skipped:0, todo:0
"""[1:]
        self._do_test(input, expected)

    def test_generator_based_fixtures_are_scoped(self):
        input = r"""
from __future__ import with_statement
import picotest
test = picotest.new()

with test("ClassName"):
  with test("#method1()"):
    @test.fixture
    def member():
      print("# setup member")
      yield "Haruhi"
      print("# teardown member")
    #
  with test("#method2()"):
    @test("fixtures are scoped")
    def _(self, member):
      print("# not reached")

if __name__ == "__main__":
  test.run()
"""[1:]
        expected = r"""
* ClassName
  * #method1()
  * #method2()
    - [ERROR] fixtures are scoped
----------------------------------------------------------------------
[ERROR] ClassName > #method2() > fixtures are scoped
NameError: 'member': corrensponding fixture not defined.
----------------------------------------------------------------------
## total:1, passed:0, failed:0, error:1, skipped:0, todo:0
"""[1:]
        self._do_test(input, expected)

    def test_raises_error_when_generator_based_fixture_doesnt_return_generator(self):
        input = r"""
from __future__ import with_statement
import picotest
test = picotest.new()

with test("Example"):
  @test.fixture
  def team():
    return "SOS"
  #
  @test("fixture should yield")
  def _(self, team):
    print("# unreachable")

if __name__ == "__main__":
  test.run()
"""[1:]
        expected = r"""
* Example
  - [ERROR] fixture should yield
----------------------------------------------------------------------
[ERROR] Example > fixture should yield
TypeError: fixture should yield value.
----------------------------------------------------------------------
## total:1, passed:0, failed:0, error:1, skipped:0, todo:0
"""[1:]
        self._do_test(input, expected)

    def test_todo_decorator_is_available_with_fixtures(self):
        input = r"""
from __future__ import with_statement
import picotest
from picotest import todo

test = picotest.new()
@test.fixture
def member(): yield "Kyon"
@test.fixture
def team(): yield "SOS"
#
with test("Example"):
  @test("@todo is available with fixtures")
  @todo
  def _(self, member, team):
    assert 1 == 0    # expected failure
#
if __name__ == "__main__":
  test.run()
"""[1:]
        expected = r"""
* Example
  - [TODO] @todo is available with fixtures
## total:1, passed:0, failed:0, error:0, skipped:0, todo:1
"""[1:]
        self._do_test(input, expected)

    def test_TestCase_object_is_provided_when_self_specified(self):
        input = r"""
from __future__ import with_statement
try:
  import unittest2 as unittest
except ImportError:
  import unittest

import picotest

test = picotest.new()
@test.fixture
def member(self):
  self.member = "Haruhi"
  yield self.member
#
with test("Example"):
  @test("self should be provided")
  def _(self, member):
    #print("provided: self.__class__=%r" % (self.__class__,))
    print("provided: isinstance(self, unittest.TestCase)=%s" % isinstance(self, unittest.TestCase))
    assert member == "Haruhi"
    assert self.member == "Haruhi"
    print("provided: member=%r" % (member,))
#
if __name__ == "__main__":
  test.run()
"""[1:]
        expected = r"""
* Example
provided: isinstance(self, unittest.TestCase)=True
provided: member='Haruhi'
  - [passed] self should be provided
## total:1, passed:1, failed:0, error:0, skipped:0, todo:0
"""[1:]
        self._do_test(input, expected)

    def test_for_statement_is_available_instead_of_with_statement(self):
        input = r"""
import picotest
test = picotest.new()

@test.fixture
def member(): yield "Haruhi"
@test.fixture
def group(): yield "SOS"
#
for _ in test("ClassName"):
  for _ in test("#method1()"):
    @test.before
    def _(self):
      self.name = "Sasaki"
    #
    @test("1+1 should be 2")
    def _():
      assert 1+1 == 2
    @test("1-1 should be 0")
    def _():
      assert 1-1 == 2    # failed
    #
    @test("begin/after is available")
    def _(self):
      assert self.name == "Sasaki"
    #
    @test("fixture injection is available")
    def _(self, member):
      assert member == "Haruhi"
#
if __name__ == "__main__":
  test.run()
"""[1:]
        expected = r"""
* ClassName
  * #method1()
    - [passed] 1+1 should be 2
    - [Failed] 1-1 should be 0
    - [passed] begin/after is available
    - [passed] fixture injection is available
----------------------------------------------------------------------
[Failed] ClassName > #method1() > 1-1 should be 0
  File "_test_pico.py", line 20, in _
    assert 1-1 == 2    # failed
AssertionError
----------------------------------------------------------------------
## total:4, passed:3, failed:1, error:0, skipped:0, todo:0
"""[1:]
        self._do_test(input, expected)


class MainApp_TC(unittest.TestCase):
    INPUT1 = r"""
from __future__ import with_statement
import picotest
test = picotest.new()
#
with test("ClassNameA"):
  with test("#method1()"):
    @test("1+1 should be 2")
    def _():
      assert 1+1==2
    @test("1-1 should be 0")
    def _():
      assert 1-1==0
  with test("#method2()"):
    @test("1*1 should be 1")
    def _():
      assert 1*1==2
    @test("1/1 should be 1")
    def _():
      assert 1/0==0
#
with test("ClassNameB"):
  with test("#method9()"):
    @test("3*3 should be 9")
    def _():
      picotest.skip_when(True, "REASON#1")
    #
    test.TODO("3**3 should be 27")
#
if __name__ == '__main__':
  picotest.main()
"""[1:]
    INPUT2 = r"""
from __future__ import with_statement
import picotest
test = picotest.new()
#
@test("2+2 should be 4")
def _():
  assert 2+2 == 4
#
if __name__ == '__main__':
  picotest.main()
"""[1:]

    EXPECTED_VERBOSE = r"""
* ClassNameA
  * #method1()
    - [passed] 1+1 should be 2
    - [passed] 1-1 should be 0
  * #method2()
    - [Failed] 1*1 should be 1
    - [ERROR] 1/1 should be 1
* ClassNameB
  * #method9()
    - [Skipped] 3*3 should be 9 (reason: REASON#1)
    - [TODO] 3**3 should be 27
"""[1:]
    EXPECTED_ERROR = r"""
----------------------------------------------------------------------
[Failed] ClassNameA > #method2() > 1*1 should be 1
  File "_test_tmp.d/ex1_test.py", line 16, in _
    assert 1*1==2
AssertionError
----------------------------------------------------------------------
[ERROR] ClassNameA > #method2() > 1/1 should be 1
  File "_test_tmp.d/ex1_test.py", line 19, in _
    assert 1/0==0
ZeroDivisionError: integer division or modulo by zero
----------------------------------------------------------------------
"""[1:]
    EXPECTED_FOOTER = r"""
## total:7, passed:3, failed:1, error:1, skipped:1, todo:1
"""[1:]

    HELP_MESSAGE = r"""
Usage: python -m picotest [options] [file or directory...]
  -h, --help   show help
  -v           verion of picotest.py
  -s STYLE     reporting style (plain/simple/verbose, or p/s/v)
  -D           print full backtrace when failed or error
  --test=NAME  specify test name to do
"""[1:]

    if with_statement_not_available:
        INPUT1 = _convert_with_statement_into_for_statement(INPUT1)
        INPUT2 = _convert_with_statement_into_for_statement(INPUT2)

    def setUp(self):
        self.testdir = "_test_tmp.d"
        os.mkdir(self.testdir)
        f = open("%s/%s" % (self.testdir, "ex1_test.py"), "w"); f.write(self.INPUT1); f.close()
        f = open("%s/%s" % (self.testdir, "ex2_test.py"), "w"); f.write(self.INPUT2); f.close()

    def tearDown(self):
        shutil.rmtree(self.testdir)

    def _picotest(self, option_str, expected_out, expected_status_code=0):
        python = sys.executable
        if option_str.startswith("-") and not option_str.startswith("-m"):
            command = "%s -m picotest %s" % (python, option_str)
        else:
            command = "%s %s" % (python, option_str)
        out, err, status_code = _run(command)
        if python3:
            out = out.decode('utf-8')
            err = err.decode('utf-8')
        out = re.sub(r'File ".*?/picotest.py", line \d+', 'File ".../picotest.py", line 000', out)
        if python31:
            out = re.sub('ZeroDivisionError: int division or modulo by zero',
                         'ZeroDivisionError: integer division or modulo by zero', out)
        elif python3:
            out = re.sub('ZeroDivisionError: division by zero',
                         'ZeroDivisionError: integer division or modulo by zero', out)
        if expected_out is not False:
            self.assertTextEqual("", err)
            self.assertTextEqual(expected_out, out)
            self.assertEqual(expected_status_code, status_code)
        return out, err, status_code

    def test_option_h(self):
        expected = self.HELP_MESSAGE
        self._picotest("-h",  expected, 0)
        self._picotest("--help", expected, 0)

    def test_option_v(self):
        expected = picotest.__version__ + "\n"
        self._picotest("-v", expected, 0)

    def test_option_s_verbose(self):
        expected = r"""
#### _test_tmp.d/ex1_test.py
"""[1:] + self.EXPECTED_VERBOSE \
        + self.EXPECTED_ERROR + r"""
#### _test_tmp.d/ex2_test.py
- [passed] 2+2 should be 4
"""[1:] + self.EXPECTED_FOOTER
        self._picotest("-s verbose _test_tmp.d/*.py", expected, 2)
        self._picotest("-sv _test_tmp.d/*.py", expected, 2)

    def test_option_s_simple(self):
        expected = ("_test_tmp.d/ex1_test.py: ..fEst\n" +
                    self.EXPECTED_ERROR +
                    "_test_tmp.d/ex2_test.py: .\n" +
                    self.EXPECTED_FOOTER)
        self._picotest("-s simple _test_tmp.d/*.py", expected, 2)
        self._picotest("-ss _test_tmp.d/*.py", expected, 2)

    def test_option_s_plain(self):
        expected = ("..fEst\n" +
                    self.EXPECTED_ERROR +
                    ".\n" +
                    self.EXPECTED_FOOTER)
        self._picotest("-s plain _test_tmp.d/*.py", expected, 2)
        self._picotest("-sp _test_tmp.d/*.py", expected, 2)

    def test_option_D(self):
        expected = (
            '_test_tmp.d/ex1_test.py: ..fEst\n'
            '----------------------------------------------------------------------\n'
            '[Failed] ClassNameA > #method2() > 1*1 should be 1\n'
            '  File ".../picotest.py", line 000, in _run_spec\n'
            '    func(*args)\n'
            '  File "_test_tmp.d/ex1_test.py", line 16, in _\n'
            '    assert 1*1==2\n'
            'AssertionError\n'
            '----------------------------------------------------------------------\n'
            '[ERROR] ClassNameA > #method2() > 1/1 should be 1\n'
            '  File ".../picotest.py", line 000, in _run_spec\n'
            '    func(*args)\n'
            '  File "_test_tmp.d/ex1_test.py", line 19, in _\n'
            '    assert 1/0==0\n'
            'ZeroDivisionError: integer division or modulo by zero\n'
            '----------------------------------------------------------------------\n'
            '_test_tmp.d/ex2_test.py: .\n'
            ) + self.EXPECTED_FOOTER
        self._picotest("-Ds simple _test_tmp.d/*.py", expected, 2)

    def test_option_test(self):
        expected = (
            '.\n'
            '## total:1, passed:1, failed:0, error:0, skipped:0, todo:0\n'
            )
        self._picotest("-sp --test='1-1 should be 0' _test_tmp.d/*.py", expected, 0)
        expected = (
            '_test_tmp.d/ex1_test.py: f\n'
            '----------------------------------------------------------------------\n'
            '[Failed] ClassNameA > #method2() > 1*1 should be 1\n'
            '  File "_test_tmp.d/ex1_test.py", line 16, in _\n'
            '    assert 1*1==2\n'
            'AssertionError\n'
            '----------------------------------------------------------------------\n'
            '_test_tmp.d/ex2_test.py: \n'
            '## total:1, passed:0, failed:1, error:0, skipped:0, todo:0\n'
            )
        self._picotest("-ss --test='1*1 should be 1' _test_tmp.d/*.py", expected, 1)

    def test_read_files_under_directry_recursively(self):
        expected = \
            "..fEst\n" \
            + self.EXPECTED_ERROR \
            + ".\n" \
            + self.EXPECTED_FOOTER
        self._picotest("-m picotest _test_tmp.d", expected, 2)

    def test_default_style_is_verbose_when_invoked_without_m_picotest(self):
        expected = \
            "#### _test_tmp.d/ex1_test.py\n" \
            + self.EXPECTED_VERBOSE \
            + self.EXPECTED_ERROR \
            + "#### _test_tmp.d/ex2_test.py\n" \
            + "- [passed] 2+2 should be 4\n" \
            + self.EXPECTED_FOOTER
        self._picotest("_test_tmp.d/*.py", expected, 2)

    def test_default_style_is_plain_when_invoked_with_m_picotest(self):
        expected = \
            "..fEst\n" \
            + self.EXPECTED_ERROR \
            + ".\n" \
            + self.EXPECTED_FOOTER
        self._picotest("-m picotest _test_tmp.d/*.py", expected, 2)

    def test_error_when_unknown_option(self):
        expected = r"""
Usage: picotest.py [options]

picotest.py: error: no such option: -x
"""[1:]
        if python24: expected = expected.replace("Usage:", "usage:")
        out, err, status_code = self._picotest("-x", False)
        self.assertTextEqual("", out)
        self.assertTextEqual(expected, err)
        #self.assertEqual(2, status_code)
        self.assertNotEqual(0, status_code)

    def test_error_when_unknown_style(self):
        expected = r"""
Usage: picotest.py [options]

picotest.py: error: -s default: unknown style (expected: verbose/simple/plain, or v/s/p)
"""[1:]
        if python24: expected = expected.replace("Usage:", "usage:")
        out, err, status_code = self._picotest("-sdefault", False)
        self.assertTextEqual("", out)
        self.assertTextEqual(expected, err)
        #self.assertEqual(2, status_code)
        self.assertNotEqual(0, status_code)

    def test_error_when_file_not_found(self):
        expected = r"""
Usage: picotest.py [options]

picotest.py: error: not-exist-file.xxx: file or directory not found.
"""[1:]
        if python24: expected = expected.replace("Usage:", "usage:")
        out, err, status_code = self._picotest("-m picotest not-exist-file.xxx", False)
        self.assertTextEqual("", out)
        self.assertTextEqual(expected, err)
        #self.assertEqual(2, status_code)
        self.assertNotEqual(0, status_code)


if __name__ == '__main__':
    unittest.main()
