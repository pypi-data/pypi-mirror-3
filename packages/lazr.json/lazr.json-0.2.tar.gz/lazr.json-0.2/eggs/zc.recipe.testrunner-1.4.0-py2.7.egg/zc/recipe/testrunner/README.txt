Test-Runner Recipe
==================

The test-runner recipe, zc.recipe.testrunner, creates a test runner
for a project.

The test-runner recipe has several options:

eggs
    The eggs option specified a list of eggs to test given as one ore
    more setuptools requirement strings.  Each string must be given on
    a separate line.

script
    The script option gives the name of the script to generate, in the
    buildout bin directory.  Of the option isn't used, the part name
    will be used.

extra-paths
    One or more extra paths to include in the generated test script.

defaults
    The defaults option lets you specify testrunner default
    options. These are specified as Python source for an expression
    yielding a list, typically a list literal.

working-directory
    The working-directory option lets to specify a directory where the
    tests will run. The testrunner will change to this directory when
    run. If the working directory is the empty string or not specified
    at all, the recipe will create a working directory among the parts.

environment
    A set of environment variables that should be exported before
    starting the tests.

initialization
    Provide initialization code to run before running tests.

relative-paths
    Use egg, test, and working-directory paths relative to the test script.

include-site-packages
    You can choose to have the site-packages of the underlying Python
    available to your script or interpreter, in addition to the packages
    from your eggs.  See `the z3c.recipe.scripts documentation`_ for
    motivations and warnings.

allowed-eggs-from-site-packages
    Sometimes you need or want to control what eggs from site-packages are
    used. The allowed-eggs-from-site-packages option allows you to specify a
    whitelist of project names that may be included from site-packages.  You
    can use globs to specify the value.  It defaults to a single value of '*',
    indicating that any package may come from site-packages.

    Here's a usage example::

        [buildout]
        ...

        allowed-eggs-from-site-packages =
            demo
            bigdemo
            zope.*

    This option interacts with the ``include-site-packages`` option in the
    following ways.

    If ``include-site-packages`` is true, then
    ``allowed-eggs-from-site-packages`` filters what eggs from site-packages
    may be chosen.  Therefore, if ``allowed-eggs-from-site-packages`` is an
    empty list, then no eggs from site-packages are chosen, but site-packages
    will still be included at the end of path lists.

    If ``include-site-packages`` is false, the value of
    ``allowed-eggs-from-site-packages`` is irrelevant.

extends
    You can extend another section using this value.  It is intended to help
    you avoid repeating yourself.

exec-sitecustomize
    Normally the Python's real sitecustomize module is not processed.
    If you want it to be processed, set this value to 'true'.  This will
    be honored irrespective of the setting for include-site-packages.

.. _`the z3c.recipe.scripts documentation`:
    http://pypi.python.org/pypi/z3c.recipe.scripts#including-site-packages-and-sitecustomize

(Note that, at this time, due to limitations in the Zope test runner, the
distributions cannot be zip files. TODO: Fix the test runner!)

To illustrate this, we'll create a pair of projects in our sample
buildout:

    >>> mkdir(sample_buildout, 'demo')
    >>> mkdir(sample_buildout, 'demo', 'demo')
    >>> write(sample_buildout, 'demo', 'demo', '__init__.py', '')
    >>> write(sample_buildout, 'demo', 'demo', 'tests.py',
    ... '''
    ... import unittest
    ...
    ... class TestDemo(unittest.TestCase):
    ...    def test(self):
    ...        pass
    ...
    ... def test_suite():
    ...     return unittest.makeSuite(TestDemo)
    ... ''')

    >>> write(sample_buildout, 'demo', 'setup.py',
    ... """
    ... from setuptools import setup
    ...
    ... setup(name = "demo")
    ... """)

    >>> write(sample_buildout, 'demo', 'README.txt', '')

    >>> mkdir(sample_buildout, 'demo2')
    >>> mkdir(sample_buildout, 'demo2', 'demo2')
    >>> write(sample_buildout, 'demo2', 'demo2', '__init__.py', '')
    >>> write(sample_buildout, 'demo2', 'demo2', 'tests.py',
    ... '''
    ... import unittest
    ...
    ... class Demo2Tests(unittest.TestCase):
    ...    def test2(self):
    ...        pass
    ...
    ... def test_suite():
    ...     return unittest.makeSuite(Demo2Tests)
    ... ''')

    >>> write(sample_buildout, 'demo2', 'setup.py',
    ... """
    ... from setuptools import setup
    ...
    ... setup(name = "demo2", install_requires= ['demoneeded'])
    ... """)

    >>> write(sample_buildout, 'demo2', 'README.txt', '')

Demo 2 depends on demoneeded:

    >>> mkdir(sample_buildout, 'demoneeded')
    >>> mkdir(sample_buildout, 'demoneeded', 'demoneeded')
    >>> write(sample_buildout, 'demoneeded', 'demoneeded', '__init__.py', '')
    >>> write(sample_buildout, 'demoneeded', 'demoneeded', 'tests.py',
    ... '''
    ... import unittest
    ...
    ... class TestNeeded(unittest.TestCase):
    ...    def test_needed(self):
    ...        pass
    ...
    ... def test_suite():
    ...     return unittest.makeSuite(TestNeeded)
    ... ''')

    >>> write(sample_buildout, 'demoneeded', 'setup.py',
    ... """
    ... from setuptools import setup
    ...
    ... setup(name = "demoneeded")
    ... """)

    >>> write(sample_buildout, 'demoneeded', 'README.txt', '')

We'll update our buildout to install the demo project as a
develop egg and to create the test script:

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... develop = demo demoneeded demo2
    ... parts = testdemo
    ... offline = true
    ...
    ... [testdemo]
    ... recipe = zc.recipe.testrunner
    ... eggs =
    ...    demo
    ...    demo2
    ... script = test
    ... """)

Note that we specified both demo and demo2 in the eggs
option and that we put them on separate lines.

We also specified the offline option to run the buildout in offline mode.

Now when we run the buildout:

    >>> import os
    >>> os.chdir(sample_buildout)
    >>> print system(os.path.join(sample_buildout, 'bin', 'buildout') + ' -q'),

We get a test script installed in our bin directory:

    >>> ls(sample_buildout, 'bin')
    -  buildout
    -  test

We also get a "testdemo" parts directory:

    >>> ls(sample_buildout, 'parts')
    d  buildout
    d  testdemo

The testdemo directory has a "working-directory," in which tests are run.
(The site-packages directory is support for the test script.)

    >>> ls(sample_buildout, 'parts', 'testdemo')
    d  site-packages
    d  working-directory

Updating leaves its contents intact:

    >>> _ = system(os.path.join(sample_buildout, 'bin', 'test') +
    ...            ' -q --coverage=coverage')
    >>> ls(sample_buildout, 'parts', 'testdemo', 'working-directory')
    d  coverage
    >>> print system(os.path.join(sample_buildout, 'bin', 'buildout') + ' -q'),
    >>> ls(sample_buildout, 'parts', 'testdemo', 'working-directory')
    d  coverage

We can run the test script to run our demo test:

    >>> print system(os.path.join(sample_buildout, 'bin', 'test') + ' -vv'),
    Running tests at level 1
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in 0.001 seconds.
      Running:
     test (demo.tests.TestDemo)
     test2 (demo2.tests.Demo2Tests)
      Ran 2 tests with 0 failures and 0 errors in 0.000 seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in 0.001 seconds.

Note that we didn't run the demoneeded tests.  Tests are only run for
the eggs listed, not for their dependencies.

If we leave the script option out of the configuration, then the test
script will get it's name from the part:

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... develop = demo
    ... parts = testdemo
    ... offline = true
    ...
    ... [testdemo]
    ... recipe = zc.recipe.testrunner
    ... eggs = demo
    ... """)

    >>> print system(os.path.join(sample_buildout, 'bin', 'buildout') + ' -q'),

    >>> ls(sample_buildout, 'bin')
    -  buildout
    -  testdemo

We can run the test script to run our demo test:

    >>> print system(os.path.join(sample_buildout, 'bin', 'testdemo') + ' -q'),
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in 0.001 seconds.
      Ran 1 tests with 0 failures and 0 errors in 0.001 seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in 0.001 seconds.

If we need to include other paths in our test script, we can use the
extra-paths option to specify them:

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... develop = demo
    ... parts = testdemo
    ... offline = true
    ...
    ... [testdemo]
    ... recipe = zc.recipe.testrunner
    ... eggs = demo
    ... extra-paths = /usr/local/zope/lib/python
    ... """)

    >>> print system(os.path.join(sample_buildout, 'bin', 'buildout') + ' -q'),

    >>> cat(sample_buildout, 'parts', 'testdemo', 'site-packages', 'site.py')
    ... # doctest: +ELLIPSIS
    "...
    def addsitepackages(known_paths):
        """Add site packages, as determined by zc.buildout.
    <BLANKLINE>
        See original_addsitepackages, below, for the original version."""
        buildout_paths = [
            '/sample-buildout/demo',
            '/sample-buildout/eggs/zope.testrunner-4.0-py2.3.egg',
            '/sample-buildout/eggs/zope.interface-3.4.1-py2.4.egg',
            '/sample-buildout/eggs/zope.exceptions-3.5.2-py2.4.egg',
            '/sample-buildout/eggs/setuptools-0.6-py1.3.egg',
            '/usr/local/zope/lib/python'
            ]
    ...

We can use the working-directory option to specify a working
directory:

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... develop = demo
    ... parts = testdemo
    ... offline = true
    ...
    ... [testdemo]
    ... recipe = zc.recipe.testrunner
    ... eggs = demo
    ... extra-paths = /usr/local/zope/lib/python
    ... working-directory = /foo/bar
    ... """)

    >>> print system(os.path.join(sample_buildout, 'bin', 'buildout') + ' -q'),

    >>> cat(sample_buildout, 'bin', 'testdemo')
    #!/usr/local/bin/python2.4 -S
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
        '/sample-buildout/parts/testdemo/site-packages',
        ]
    <BLANKLINE>
    <BLANKLINE>
    import os
    path = sys.path[0]
    if os.environ.get('PYTHONPATH'):
        path = os.pathsep.join([path, os.environ['PYTHONPATH']])
    os.environ['PYTHONPATH'] = path
    import site # imports custom buildout-generated site.py
    import os
    sys.argv[0] = os.path.abspath(sys.argv[0])
    os.chdir('/foo/bar')
    <BLANKLINE>
    import zope.testrunner
    <BLANKLINE>
    if __name__ == '__main__':
        zope.testrunner.run([
            '--test-path', '/sample-buildout/demo',
            ])

Now that our tests use a specified working directory, their designated
part directory is gone:

    >>> ls(sample_buildout, 'parts', 'testdemo')
    d  site-packages


If we need to specify default options, we can use the defaults
option. For example, Zope 3 applications typically define test suites
in modules named ftests or tests.  The default test runner behaviour
is to look in modules named tests.  To specify that we want to look in
tests and ftests module, we'd supply a default for the --tests-pattern
option.  If we like dots, we could also request more verbose output
using the -v option:

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... develop = demo
    ... parts = testdemo
    ... offline = true
    ...
    ... [testdemo]
    ... recipe = zc.recipe.testrunner
    ... eggs = demo
    ... extra-paths = /usr/local/zope/lib/python
    ... defaults = ['--tests-pattern', '^f?tests$',
    ...             '-v'
    ...            ]
    ... """)

    >>> print system(os.path.join(sample_buildout, 'bin', 'buildout') + ' -q'),

    >>> cat(sample_buildout, 'bin', 'testdemo')
    #!/usr/local/bin/python2.4 -S
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
        '/sample-buildout/parts/testdemo/site-packages',
        ]
    <BLANKLINE>
    <BLANKLINE>
    import os
    path = sys.path[0]
    if os.environ.get('PYTHONPATH'):
        path = os.pathsep.join([path, os.environ['PYTHONPATH']])
    os.environ['PYTHONPATH'] = path
    import site # imports custom buildout-generated site.py
    import os
    sys.argv[0] = os.path.abspath(sys.argv[0])
    os.chdir('/sample-buildout/parts/testdemo/working-directory')
    <BLANKLINE>
    import zope.testrunner
    <BLANKLINE>
    if __name__ == '__main__':
        zope.testrunner.run((['--tests-pattern', '^f?tests$',
    '-v'
    ]) + [
            '--test-path', '/sample-buildout/demo',
            ])


Some things to note from this example:

- Parentheses are placed around the given expression.

- Leading whitespace is removed.


To demonstrate the ``environment`` option, we first update the tests to
include a check for an environment variable:

    >>> write(sample_buildout, 'demo', 'demo', 'tests.py',
    ... '''
    ... import unittest
    ... import os
    ...
    ... class DemoTests(unittest.TestCase):
    ...    def test(self):
    ...        self.assertEquals('42', os.environ.get('zc.recipe.testrunner', '23'))
    ...
    ... def test_suite():
    ...     return unittest.makeSuite(DemoTests)
    ... ''')

Running them with the current buildout will produce a failure:

    >>> print system(os.path.join(sample_buildout, 'bin', 'testdemo') + ' -vv'), # doctest: +ELLIPSIS
    Running tests at level 1
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in 0.001 seconds.
      Running:
     test (demo.tests.DemoTests) (0.000 s)
    <BLANKLINE>
    <BLANKLINE>
    Failure in test test (demo.tests.DemoTests)
    Traceback (most recent call last):
      ...
    AssertionError: '42' != '23'
    <BLANKLINE>
    <BLANKLINE>
      Ran 1 tests with 1 failures and 0 errors in 0.001 seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in 0.001 seconds.
    <BLANKLINE>
    Tests with failures:
       test (demo.tests.DemoTests)


Let's update the buildout to specify the environment variable for the test
runner:

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... develop = demo
    ... parts = testdemo
    ... offline = true
    ...
    ... [testdemo]
    ... recipe = zc.recipe.testrunner
    ... eggs = demo
    ... environment = testenv
    ...
    ... [testenv]
    ... zc.recipe.testrunner = 42
    ... """)

We run buildout and see that the test runner script now includes setting up
the environment variable. Also, the tests pass again:

    >>> print system(os.path.join(sample_buildout, 'bin', 'buildout') + ' -q'),

    >>> cat(sample_buildout, 'bin', 'testdemo')
    #!/usr/local/bin/python2.4 -S
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
        '/sample-buildout/parts/testdemo/site-packages',
        ]
    <BLANKLINE>
    <BLANKLINE>
    import os
    path = sys.path[0]
    if os.environ.get('PYTHONPATH'):
        path = os.pathsep.join([path, os.environ['PYTHONPATH']])
    os.environ['PYTHONPATH'] = path
    import site # imports custom buildout-generated site.py
    import os
    sys.argv[0] = os.path.abspath(sys.argv[0])
    os.chdir('/sample-buildout/parts/testdemo/working-directory')
    os.environ['zc.recipe.testrunner'] = '42'
    <BLANKLINE>
    import zope.testrunner
    <BLANKLINE>
    if __name__ == '__main__':
        zope.testrunner.run([
            '--test-path', '/sample-buildout/demo',
            ])

    >>> print system(os.path.join(sample_buildout, 'bin', 'testdemo') + ' -vv'),
    Running tests at level 1
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in 0.001 seconds.
      Running:
     test (demo.tests.DemoTests)
      Ran 1 tests with 0 failures and 0 errors in 0.001 seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in 0.001 seconds.

One can add initialization steps in the buildout.  These will be added to the
end of the script:

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... develop = demo
    ... parts = testdemo
    ... offline = true
    ...
    ... [testdemo]
    ... recipe = zc.recipe.testrunner
    ... eggs = demo
    ... extra-paths = /usr/local/zope/lib/python
    ... defaults = ['--tests-pattern', '^f?tests$',
    ...             '-v'
    ...            ]
    ... initialization = print 'Hello all you egg-laying pythons!'
    ... """)

    >>> print system(os.path.join(sample_buildout, 'bin', 'buildout') + ' -q'),

    >>> cat(sample_buildout, 'bin', 'testdemo')
    #!/usr/local/bin/python2.4 -S
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
        '/sample-buildout/parts/testdemo/site-packages',
        ]
    <BLANKLINE>
    <BLANKLINE>
    import os
    path = sys.path[0]
    if os.environ.get('PYTHONPATH'):
        path = os.pathsep.join([path, os.environ['PYTHONPATH']])
    os.environ['PYTHONPATH'] = path
    import site # imports custom buildout-generated site.py
    import os
    sys.argv[0] = os.path.abspath(sys.argv[0])
    os.chdir('/sample-buildout/parts/testdemo/working-directory')
    print 'Hello all you egg-laying pythons!'
    <BLANKLINE>
    import zope.testrunner
    <BLANKLINE>
    if __name__ == '__main__':
        zope.testrunner.run((['--tests-pattern', '^f?tests$',
    '-v'
    ]) + [
            '--test-path', '/sample-buildout/demo',
            ])

This will also work with a multi-line initialization section:

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... develop = demo
    ... parts = testdemo
    ... offline = true
    ...
    ... [testdemo]
    ... recipe = zc.recipe.testrunner
    ... eggs = demo
    ... extra-paths = /usr/local/zope/lib/python
    ... defaults = ['--tests-pattern', '^f?tests$',
    ...             '-v'
    ...            ]
    ... initialization = print 'Hello all you egg-laying pythons!'
    ...                  print 'I thought pythons were live bearers?'
    ... """)

    >>> print system(os.path.join(sample_buildout, 'bin', 'buildout') + ' -q'),

    >>> cat(sample_buildout, 'bin', 'testdemo')
    #!/usr/local/bin/python2.4 -S
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
        '/sample-buildout/parts/testdemo/site-packages',
        ]
    <BLANKLINE>
    <BLANKLINE>
    import os
    path = sys.path[0]
    if os.environ.get('PYTHONPATH'):
        path = os.pathsep.join([path, os.environ['PYTHONPATH']])
    os.environ['PYTHONPATH'] = path
    import site # imports custom buildout-generated site.py
    import os
    sys.argv[0] = os.path.abspath(sys.argv[0])
    os.chdir('/sample-buildout/parts/testdemo/working-directory')
    print 'Hello all you egg-laying pythons!'
    print 'I thought pythons were live bearers?'
    <BLANKLINE>
    import zope.testrunner
    <BLANKLINE>
    if __name__ == '__main__':
        zope.testrunner.run((['--tests-pattern', '^f?tests$',
    '-v'
    ]) + [
            '--test-path', '/sample-buildout/demo',
            ])

If the relative-paths option is used, egg (and extra) paths are
generated relative to the test script.

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... develop = demo
    ... parts = testdemo
    ... offline = true
    ...
    ... [testdemo]
    ... recipe = zc.recipe.testrunner
    ... eggs = demo
    ... extra-paths = /usr/local/zope/lib/python
    ...               ${buildout:directory}/sources
    ... relative-paths = true
    ... """)

    >>> print system(os.path.join(sample_buildout, 'bin', 'buildout') + ' -q'),

    >>> cat(sample_buildout, 'bin', 'testdemo')
    #!/usr/local/bin/python2.4 -S
    <BLANKLINE>
    import os
    <BLANKLINE>
    join = os.path.join
    base = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
    base = os.path.dirname(base)
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
        join(base, 'parts/testdemo/site-packages'),
        ]
    <BLANKLINE>
    <BLANKLINE>
    import os
    path = sys.path[0]
    if os.environ.get('PYTHONPATH'):
        path = os.pathsep.join([path, os.environ['PYTHONPATH']])
    os.environ['PYTHONPATH'] = path
    import site # imports custom buildout-generated site.py
    import os
    sys.argv[0] = os.path.abspath(sys.argv[0])
    os.chdir(join(base, 'parts/testdemo/working-directory'))
    <BLANKLINE>
    import zope.testrunner
    <BLANKLINE>
    if __name__ == '__main__':
        zope.testrunner.run([
            '--test-path', join(base, 'demo'),
            ])

    >>> cat(sample_buildout, 'parts', 'testdemo', 'site-packages', 'site.py')
    ... # doctest: +ELLIPSIS
    "...
    def addsitepackages(known_paths):
        """Add site packages, as determined by zc.buildout.
    <BLANKLINE>
        See original_addsitepackages, below, for the original version."""
        join = os.path.join
        base = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
        base = os.path.dirname(base)
        base = os.path.dirname(base)
        base = os.path.dirname(base)
        buildout_paths = [
            join(base, 'demo'),
            join(base, 'eggs/zope.testrunner-4.0.0-py2.4.egg'),
            join(base, 'eggs/zope.interface-3.5.1-py2.4-linux-i686.egg'),
            join(base, 'eggs/zope.exceptions-3.5.2-linux-i686.egg'),
            join(base, 'eggs/setuptools-0.6c9-py2.4.egg'),
            '/usr/local/zope/lib/python',
            join(base, 'sources')
            ]
    ...

The relative-paths option can be specified at the buildout level:

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... develop = demo
    ... parts = testdemo
    ... offline = true
    ... relative-paths = true
    ...
    ... [testdemo]
    ... recipe = zc.recipe.testrunner
    ... eggs = demo
    ... extra-paths = /usr/local/zope/lib/python
    ...               ${buildout:directory}/sources
    ... """)

    >>> print system(os.path.join(sample_buildout, 'bin', 'buildout') + ' -q'),

    >>> cat(sample_buildout, 'bin', 'testdemo')
    #!/usr/local/bin/python2.4 -S
    <BLANKLINE>
    import os
    <BLANKLINE>
    join = os.path.join
    base = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
    base = os.path.dirname(base)
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
        join(base, 'parts/testdemo/site-packages'),
        ]
    <BLANKLINE>
    <BLANKLINE>
    import os
    path = sys.path[0]
    if os.environ.get('PYTHONPATH'):
        path = os.pathsep.join([path, os.environ['PYTHONPATH']])
    os.environ['PYTHONPATH'] = path
    import site # imports custom buildout-generated site.py
    import os
    sys.argv[0] = os.path.abspath(sys.argv[0])
    os.chdir(join(base, 'parts/testdemo/working-directory'))
    <BLANKLINE>
    import zope.testrunner
    <BLANKLINE>
    if __name__ == '__main__':
        zope.testrunner.run([
            '--test-path', join(base, 'demo'),
            ])

-------------------------
Support for system Python
-------------------------

zc.recipe.testrunner 1.4.0 added support for zc.buildout 1.5's system Python
support.

By default, this means that, if the buildout is set up as described in the
`pertinent section of the zc.buildout documentation`_ then the scripts
generated by this recipe will be safe to use with a system Python.

You can also use the same options as provided by z3c.recipe.scripts (and
the functionality is delegated to code from this package).  That package
is well-tested, so this merely quickly demonstrates usage.

include-site-packages
---------------------

Use this to include site-packages from the Python you are using.

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... develop = demo
    ... parts = testdemo
    ... offline = true
    ...
    ... [testdemo]
    ... recipe = zc.recipe.testrunner
    ... eggs = demo
    ... include-site-packages = true
    ... """)

.. ReST comment: Hide the rest of the test from PyPI readers.

    >>> ignore = system(
    ...     os.path.join(sample_buildout, 'bin', 'buildout') + ' -q'),

    >>> cat(sample_buildout, 'parts', 'testdemo', 'site-packages', 'site.py')
    ... # doctest: +ELLIPSIS
    "...
    def addsitepackages(known_paths):
        """Add site packages, as determined by zc.buildout.
    <BLANKLINE>
        See original_addsitepackages, below, for the original version."""
        setuptools_path = '...'
        sys.path.append(setuptools_path)
        known_paths.add(os.path.normcase(setuptools_path))
        import pkg_resources
        buildout_paths = [
            '/sample-buildout/demo',
            '/sample-buildout/eggs/zope.testrunner-4.0-py2.3.egg',
            '/sample-buildout/eggs/zope.exceptions-3.4.1-py2.4.egg'
            ]
        for path in buildout_paths:
            sitedir, sitedircase = makepath(path)
            if not sitedircase in known_paths and os.path.exists(sitedir):
                sys.path.append(sitedir)
                known_paths.add(sitedircase)
                pkg_resources.working_set.add_entry(sitedir)
        sys.__egginsert = len(buildout_paths) # Support distribute.
        original_paths = [
            ...
            ]
        for path in original_paths:
            if path == setuptools_path or path not in known_paths:
                addsitedir(path, known_paths)
        return known_paths
    ...

Note that a setting in the buildout section will also be honored, if it is
not overridden locally.

.. ReST comment: Hide the test from PyPI readers.

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... develop = demo
    ... parts = testdemo
    ... offline = true
    ... include-site-packages = true
    ...
    ... [testdemo]
    ... recipe = zc.recipe.testrunner
    ... eggs = demo
    ... """)

    >>> ignore = system(
    ...     os.path.join(sample_buildout, 'bin', 'buildout') + ' -q'),

    >>> cat(sample_buildout, 'parts', 'testdemo', 'site-packages', 'site.py')
    ... # doctest: +ELLIPSIS
    "...
    def addsitepackages(known_paths):
        """Add site packages, as determined by zc.buildout.
    <BLANKLINE>
        See original_addsitepackages, below, for the original version."""
        setuptools_path = '...'
        sys.path.append(setuptools_path)
        known_paths.add(os.path.normcase(setuptools_path))
        import pkg_resources
        buildout_paths = [
            '/sample-buildout/demo',
            '/sample-buildout/eggs/zope.testrunner-4.0-py2.3.egg',
            '/sample-buildout/eggs/zope.exceptions-3.4.1-py2.4.egg'
            ]
        for path in buildout_paths:
            sitedir, sitedircase = makepath(path)
            if not sitedircase in known_paths and os.path.exists(sitedir):
                sys.path.append(sitedir)
                known_paths.add(sitedircase)
                pkg_resources.working_set.add_entry(sitedir)
        sys.__egginsert = len(buildout_paths) # Support distribute.
        original_paths = [
            ...
            ]
        for path in original_paths:
            if path == setuptools_path or path not in known_paths:
                addsitedir(path, known_paths)
        return known_paths
    ...

allowed-eggs-from-site-packages
-------------------------------

allowed-eggs-from-site-packages is described at the start of this document.
It is a whitespace-delineated list of eggs that may be obtained from the
filesystem.  It may use wildcards, and it defaults to "*", accepting all
eggs.

Here's a demonstration of how you would use
allowed-eggs-from-sitepackages to allow no eggs to come from the
filesystem, but still let you import other packages (like PIL) from the
filesystem. (Note that the eggs-directory and the executable are only
part of making this documentation testable, and not necessary to use
this option.)

Imagine that the system Python has demo installed.  If
allowed-eggs-from-site-packages were its default value of '*', an
installation would succeed, because it would be found in site-packages.
However, this example would fail, because the site-packages version
would not be allowed.

.. ReST comment: unimportant for PyPI (comment ends at next "..")

    >>> py_path, site_packages_path = make_py(initialization='''\
    ... import os
    ... os.environ['zc.buildout'] = 'foo bar baz shazam'
    ... ''')
    >>> from zc.buildout.tests import create_sample_sys_install
    >>> create_sample_sys_install(site_packages_path)
    >>> new_buildout = tmpdir('new_buildout')
    >>> cd(new_buildout)
    >>> mkdir(new_buildout, 'altdemo')
    >>> mkdir(new_buildout, 'altdemo', 'demo')
    >>> write(new_buildout, 'altdemo', 'demo', '__init__.py', '')
    >>> write(new_buildout, 'altdemo', 'setup.py',
    ... """
    ... from setuptools import setup
    ...
    ... setup(name = "altdemo")
    ... """)
    >>> write(new_buildout, 'altdemo', 'README.txt', '')
    >>> from zc.buildout.testing import install_develop, make_buildout
    >>> make_buildout()
    >>> install_develop(
    ...     'zc.recipe.testrunner', os.path.join(new_buildout, 'develop-eggs'))
    >>> install_develop(
    ...     'zope.testrunner', os.path.join(new_buildout, 'develop-eggs'))
    >>> install_develop(
    ...     'zope.interface', os.path.join(new_buildout, 'develop-eggs'))
    >>> install_develop(
    ...     'zope.exceptions', os.path.join(new_buildout, 'develop-eggs'))
    >>> install_develop(
    ...     'zc.recipe.egg', os.path.join(new_buildout, 'develop-eggs'))
    >>> install_develop(
    ...     'z3c.recipe.scripts', os.path.join(new_buildout, 'develop-eggs'))

..

    >>> write(new_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... develop = altdemo
    ... parts = testdemo
    ... eggs-directory = tmpeggs
    ... executable = %(py_path)s
    ...
    ... [testdemo]
    ... recipe = zc.recipe.testrunner
    ... eggs = demo
    ... include-site-packages = true
    ... allowed-eggs-from-site-packages =
    ... """ % dict(py_path=py_path))

.. ReST comment: Hide the rest of the test from PyPI readers.

   This will fail, because we cannot find demo anywhere (notice we are no
   longer developing it in the buildout configuration above):

    >>> print system(
    ...     os.path.join(new_buildout, 'bin', 'buildout') + ' -q'),
    While:
      Installing testdemo.
      Getting distribution for 'demo'.
    Error: Couldn't find a distribution for 'demo'.

   However, if we allow all eggs through, it works, because demo has been
   installed in the "system Python".

    >>> write(new_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... develop = altdemo
    ... parts = testdemo
    ... eggs-directory = tmpeggs
    ... executable = %(py_path)s
    ... offline = true
    ...
    ... [testdemo]
    ... recipe = zc.recipe.testrunner
    ... eggs = demo
    ... include-site-packages = true
    ... """ % dict(py_path=py_path))

    >>> print system(
    ...     os.path.join(new_buildout, 'bin', 'buildout') + ' -q'),


Like include-site-packages, it is also honored in the main buildout
section if it is not overridden.

.. ReST comment: hide from PyPI.  This will fail again, showing we have
   blocked the eggs.

    >>> write(new_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... parts = testdemo
    ... eggs-directory = tmpeggs
    ... allowed-eggs-from-site-packages =
    ... executable = %(py_path)s
    ... offline = true
    ...
    ... [testdemo]
    ... recipe = zc.recipe.testrunner
    ... eggs = demo
    ... include-site-packages = true
    ... """ % dict(py_path=py_path))

    >>> print system(
    ...     os.path.join(new_buildout, 'bin', 'buildout') + ' -q'),
    While:
      Installing testdemo.
      Getting distribution for 'demo'.
    Error: Couldn't find a distribution for 'demo'.

extends
-------

The extends option lets you inherit options from other sections.  This can
keep you from repeating yourself.  For instance, in this example, the
testdemo section gets all of its configuration from the source section, except
it overrides the initialization.

.. ReST comment: we'll move back to the sample_buildout.

    >>> cd(sample_buildout)

..

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... develop = demo
    ... parts = testdemo
    ... offline = true
    ...
    ... [source]
    ... eggs = demo
    ... extra-paths = /usr/local/zope/lib/python
    ... defaults = ['--tests-pattern', '^f?tests$',
    ...             '-v'
    ...            ]
    ... initialization = print 'Hello all you egg-laying pythons!'
    ...
    ... [testdemo]
    ... recipe = zc.recipe.testrunner
    ... extends = source
    ... initialization = print 'Hello all you egg-laying pythons!'
    ...                  print 'I thought pythons were live bearers?'
    ... """)

.. ReST comment: PyPI readers don't need to see the proof, but here it is.

    >>> print system(os.path.join(sample_buildout, 'bin', 'buildout') + ' -q'),

    >>> cat(sample_buildout, 'bin', 'testdemo')
    #!/usr/local/bin/python2.4 -S
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
        '/sample-buildout/parts/testdemo/site-packages',
        ]
    <BLANKLINE>
    <BLANKLINE>
    import os
    path = sys.path[0]
    if os.environ.get('PYTHONPATH'):
        path = os.pathsep.join([path, os.environ['PYTHONPATH']])
    os.environ['PYTHONPATH'] = path
    import site # imports custom buildout-generated site.py
    import os
    sys.argv[0] = os.path.abspath(sys.argv[0])
    os.chdir('/sample-buildout/parts/testdemo/working-directory')
    print 'Hello all you egg-laying pythons!'
    print 'I thought pythons were live bearers?'
    <BLANKLINE>
    import zope.testrunner
    <BLANKLINE>
    if __name__ == '__main__':
        zope.testrunner.run((['--tests-pattern', '^f?tests$',
    '-v'
    ]) + [
            '--test-path', '/sample-buildout/demo',
            ])

exec-sitecustomize
------------------

This option lets you choose to execute the sitecustomize file of the Python
you are using.  It is usually false.

.. ReST comment: here's the demo.

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... develop = demo
    ... parts = testdemo
    ... executable = %(py_path)s
    ...
    ... [testdemo]
    ... recipe = zc.recipe.testrunner
    ... eggs = demo
    ... exec-sitecustomize = true
    ... """ % dict(py_path=py_path))

    >>> ignored = system(buildout),

    >>> cat(sample_buildout, 'parts', 'testdemo', 'site-packages',
    ...     'sitecustomize.py') # doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
    <BLANKLINE>
    # The following is from
    # /executable_buildout/parts/py/sitecustomize.py
    ...
    import os
    os.environ['zc.buildout'] = 'foo bar baz shazam'

.. _`pertinent section of the zc.buildout documentation`:
    http://pypi.python.org/pypi/zc.buildout/1.5.0#working-with-a-system-python



