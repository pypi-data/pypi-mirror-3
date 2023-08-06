""" run JavaScript unit tests from the Python test runner

    this wraps some py.test extension I wrote a while ago so that it can be
    used combined with unittest.py, and in our case the Zope test runner -
    the test runner finds this file and executes it, the py lib code takes
    care of calling Spidermonkey and executing the JS files referenced.
"""

import unittest
import os
import sys
import py
from py.__.test.outcome import Failed

here = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(here, '..', 'static'))

from jsbase import conftest

class ItemData:
    def __init__(self, fspath):
        self.fspath = fspath

class JavaScriptException(Exception):
    pass

def have_js():
    o = os.popen('js -e "print(\'works\');"')
    try:
        have_js = o.read().startswith('works')
    finally:
        o.close()
    return have_js

def get_testcase(jsfile):
    if not have_js():
        print 'spidermonkey not installed - skipping tests'
        return unittest.TestCase
    class JavaScriptTestCase(unittest.TestCase):
        pass
    jspath = py.path.local(os.path.join(here, jsfile))
    JavaScriptTestCase.__name__ = jspath.purebasename
    data = ItemData(jspath)
    checker = conftest.JSChecker(jspath, data)

    for path in checker.run():
        def get_testmethod(path, name):
            def testmethod(self):
                testclass = checker.join(path)
                try:
                    testclass.run()
                except Failed, e:
                    # XXX the eval is because the Py lib escapes slashes...
                    # really annoying, must ping fijal about it
                    raise JavaScriptException(eval(str(e)))
            testmethod.func_name = name
            return testmethod
        name = path.rsplit('/', 1)[-1]
        setattr(JavaScriptTestCase, name, get_testmethod(path, name))
    return JavaScriptTestCase


