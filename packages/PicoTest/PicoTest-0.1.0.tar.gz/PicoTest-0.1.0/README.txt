==================
PicoTest.py README
==================

Release: 0.1.0

.. contents::



Overview
========

PicoTest.py is a small but very useful testing library for Python.



Basic Example
=============

PicoTest.py uses ``with`` statement instead of ``TestCase`` class.

* Test topc or context is represented by ``with`` statement.
* Test spec is represented by ``@test`` decorator.

examples/1_basic_test.py::

    import picotest
    test = picotest.new()

    with test("assertion example"):

        @test("1+1 should be 2")
        def _():                # 'self' is not required
            assert 1+1 == 2

        @test("assertion methods of unittest are avaiable")
        def _(self):
            self.assertEqual("Haruhi".upper(), "HARUHI")

        @test("'assertTextEqual()' is available which shows diff of two texts")
        def _(self):
            expected = "\n".join(["Haruhi", "Mikuru", "Yuki"])
            actual   = "\n".join(["Haruhi", "Mikuru", "Yuki"])
            #actual   = "\n".join(["Haruhi", "Michiru", "Yuki"])
            self.assertTextEqual(expected, actual)

    if __name__ == '__main__':
        picotest.main()


Output example (verbose style)::

    $ python examples/1_basic_test.py
    * assertion example
      - [passed] 1+1 should be 2
      - [passed] assertion methods of unittest are avaiable
      - [passed] 'assertTextEqual()' is available which shows diff of two texts
    ----------------------------------------------------------------------
    ## total:3, passed:3, failed:0, error:0, skipped:0, todo:0


Output example (plain style)::

    $ python examples/1_basic_test.py -sp   # or -s plain
    ...
    ## total:3, passed:3, failed:0, error:0, skipped:0, todo:0



Test Structure
==============

Nested test structure is available.
This makes you to write tests in structured style.

examples/2_structure_test.py::

    import picotest
    test = picotest.new()

    with test("ClassName"):

        with test("#method_name()"):

            with test("when base is not specified..."):

                @test("int('11') should be 11")
                def _():
                    assert int('11') == 11

            with test("when base is specified..."):

                @test("int('11', 16) should be 17")
                def _():
                    assert int('11', 16) == 17

                @test("int('11', 8) should be 9")
                def _():
                    assert int('11', 8) == 9

                @test("int('11', 2) should be 3")
                def _():
                    assert int('11', 2) == 3

    if __name__ == '__main__':
        test.main()



Setup and Teadown Fixture
=========================

Setup and teardown fixtures are available.
They are provided by ``@test.before`` and ``@test.after`` decorators respectively.

examples/3_setup_teadown_test.py::

    import picotest
    test = picotest.new()

    with test("fixtures (setup, teardown) example"):

        @test.before    # setup    (should be defined before other tests!)
        def _(self):
            self.name = "Haruhi"
            self.team = "SOS"

        @test.after     # teardown (should be defined before other tests!)
        def _(self):
            pass

        @test("fixture should be called #1")
        def _(self):
            self.assertEqual("Haruhi", self.name)

        @test("fixture should be called #2")
        def _(self):
            self.assertEqual("SOS", self.team)

    if __name__ == '__main__':
        picotest.main()



Fixture Injection
=================

Fixture Injection is available which is more flexible than setup/teardown.

examples/4_fixture_injection_test.py::

    import os
    import picotest
    test = picotest.new()

    with test("fixture injection example"):

        @test.fixture
        def member(self):
            yield "Haruhi"     # use 'yield', not 'return'

        @test.fixture
        def team():            # 'self' is optional
            yield "SOS"

        @test("fixture is injected automatically")
        def _(self, member, team):
            assert member == "Haruhi"
            assert team   == "SOS"

        @test.fixture
        def tmpfile(self):
            ## setup temporary file
            filename = "_tmpfile.txt"
            with open(filename, "w") as f: f.write("SOS\n")
            yield filename
            ## teardown temporary file
            os.unlink(filename)

        @test("temporary file is created and removed automatically")
        def _(tmpfile):
            assert tmpfile == "_tmpfile.txt"
            with open(tmpfile) as f:
                assert f.read() == "SOS\n"

    if __name__ == '__main__':
        picotest.main()



Skip and Todo
=============

PicoTest.py supports test skip and todo.

picotest.skip_when(condition, reason)
    When condition is true then skip rest assertions.

picotest.todo
    Decorator to represents that "feature is not implemented yet".

test.TODO(description):
    Same as::

        @test("...description...")
	@todo
	def _():
	    assert False     # expected failure


example/5_skip_and_todo_test.py::

    import picotest
    from picotest import skip_when, todo
    test = picotest.new()

    with test("skip and todo example"):

        @test("skip test when condition is true")
        def _(self):
            condition = True
            skip_when(condition, "REASON")
            assert 1 == 0     # unreachable

        @test("'@todo' means 'not implemented yet'")
        @todo
        def _(self):
            assert 1 == 0    # expected failure

        test.TODO("something what you have to do #1")
        test.TODO("something what you have to do #2")

    if __name__ == '__main__':
        picotest.main()



Command-line Interface
======================

PicoTest.py provides command-line interface::

    $ python test/foo_test.py        # run test script (verbose style)
    $ python test/foo_test.py -sp    # run test script (plain style)
    $ python test/*.py               # run all test scripts
    $ python -m picotest test/*.py   # run all test scripts
    $ python -m picotest test        # run all under 'test' directory
    $ python -m picotest -h                 # show help
    $ python -m picotest -v                 # print version
    $ python -m picotest -sv test/*.py      # or -s verbose
    $ python -m picotest -ss test/*.py      # or -s simple
    $ python -m picotest -sp test/*.py      # or -s plain
    $ python -m picotest --test='...' test  # filter by description
    $ python -m picotest -D test/*.py       # show all backtrace

``picotest.main()`` exists process with status code which represens number
of failed or error tests::

    $ python examples/1_basic_test.py -sp
    ..f
    ----------------------------------------------------------------------
    [Failed] assertion example > 'assertTextEqual()' is available which shows diff of two texts
       :
    ----------------------------------------------------------------------
    ## total:3, passed:2, failed:1, error:0, skipped:0, todo:0
    $ echo $?
    1                 # number of failed or error tests



Copyright
=========

$Copyright: copyright(c) 2011 kuwata-lab.com all rights reserved $



License
=======

$License: MIT License $
