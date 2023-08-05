==============
gocept.exttest
==============

Helper to integrate external tests with python unittests.

Requirements
============

The external command needs to provide the `--list` argument, which must return
a list of available tests in a JSON datastructure::

    >>> bin/external_test_runner --list 
    ... [{"case": "MyExternalTestCase",
    ...   "tests": ["test_first_js_func", "test_second_js_func"]}

The external command needs to provide the `--run` argument to run one explicit
test::

    >>> bin/external_test_runner --run MyExternalTestCase.test_second_js_func
    ... [{"name": "MyExternalTestCase.test_second_js_func",
    ...   "status": "FAIL",
    ...   "message": "Test failed.",
    ...   "traceback": "..."}]

If none of the both arguments is provided, the external command should run all
tests::

    >>> bin/external_test_runner
    ... [{"name": "MyExternalTestCase.test_first_js_func",
    ...   "status": "SUCCESS",
    ...   "message": "Test passed."},
    ...  {"name": "MyExternalTestCase.test_second_js_func",
    ...   "status": "FAIL",
    ...   "message": "Test failed.",
    ...   "traceback": "..."}]

Usage
=====

gocept.exttest provides the method `makeSuite`, which creates a
`unittest.TestSuite` with `TestCases` for each test returned by your external
command with the `--list` argument.

If your external command needs additional arguments, you can pass them to the
`makeSuite` function as arguments.

The following setup example needs to be placed into a file, which can be found
by your testrunner::

    >>> import gocept.exttest
    ... def test_suite():
    ...     return gocept.exttest.makeSuite(
    ...         'bin/external_test_runner', '--some-arg', '--another-arg')

Example
=======

Running tests
-------------

We built gocept.exttest to integrate javascript unittests with python
unittests. Therefore, we decided to use jasmine as the javascript unittest
framework. We also use jasmine with node.js to test the javascript code browser
independent.  In order to use jasmine with gocept.exttest, we forked the
jasmine-node to be able to speak json and provide the `--list` argument.

In your buildout environment, install node.js and jasmine-node like this::

    >>> [buildout]
    ... parts =
    ...    nodejs
    ...    test
    ...
    ... [nodejs]
    ... recipe = gp.recipe.node
    ... npms = ${buildout:directory}/../jasmine-node
    ... scripts = jasmine-node
    ...
    ... [test]
    ... recipe = zc.recipe.testrunner
    ... eggs = your.package
    ... environment = env
    ...
    ... [env]
    ... jasmine-bin = ${buildout:directory}/bin/jasmine-node

You need to checkout the jasmine-node fork from
https://github.com/wosc/jasmine-node to ${buildout:directory}/../jasmine-node
until the changes are merged upstream.

Now you can run `bin/test`, which now runs the javascript unittests defined in
your.package.

Writing tests
-------------

You can write your tests either using JavaScript or CoffeeScript. In the
testrunner, you need to provide the path to your jasmine binary (from the
environment). You may also specify whether to use CoffeeScript or not::

    >>> import gocept.exttest
    ... def test_suite():
    ...    return gocept.exttest.makeSuite(
    ...        os.environ.get('jasmine-bin'),
    ...        '--coffee',
    ...        '--json',
    ...        pkg_resources.resource_filename('your.package', 'tests'))

In your package, create the folder `tests` and add your Coffee- or
JavaScript files, which need to have `_spec` in their name and can look like
this::

    >>> require 'my_app.js'
    ...
    ... describe 'MyApp', ->
    ...  it 'testname', ->
    ...    expect(new MyApp().to_test).toEqual(value)

For further documentation please read the jasmine docs.
