#!/usr/bin/env python

import os
import unittest
from StringIO import StringIO

from lxml import etree
from selenium import selenium
from mapper import SeleniumMapper

class SuiteAdaptor:
    ''' A way to obtain data from a Test Suite '''

    def __init__(self, name, tests):
        self.name = name
        self.tests = tests

    def get_suite_name(self):
        ''' Returns a string with the name for this suite '''
        return self.name

    def get_tests(self):
        ''' Returns a list of SingleTest '''
        return self.tests

class SingleTest:
    ''' Helper class to create a function that builds a test method '''

    def __init__(self, name, table):
        self.name = name
        self.table = table

    def get_name(self):
        ''' Returns the name of this test '''
        return self.name

    def get_runnable(self):
        parent_self = self
        def wrapped(self):
            for instruction in parent_self.table.findall(".//tr"):
                args = instruction.findall("td")
                # Only call text if we've got at least 3 <td>s
                if len(args) > 2:
                    args = [a.text for a in args]
                    # Add a possible documenting string
                    (len(args) > 3) or args.append('')

                    cmd = args.pop(0)
                    try:
                        self.mapper.__getattribute__(cmd)
                    except AttributeError:
                        raise PySeleneseError("Either Selenese command '%s'"+
                            " is not implemented yet, or a semantic error "+
                            "was found in the Selenese file." % cmd)
                    self.mapper.__getattribute__(cmd)(args)
        return wrapped

def _get_html_title(tree, default = "Untitled"):
    """Return a decent title from the current HTML page tree"""
    try:
        return tree.find("/head/title").text
    except AttributeError:
        return default

class TestSuiteFileAdaptor(SuiteAdaptor):
    ''' Scans a local directory for a index.html describing a test suite '''

    def __init__(self, directory):
        old_dir = os.getcwd()
        os.chdir(directory)
        p = etree.HTMLParser()
        x = etree.parse('index.html', p)

        self.name = _get_html_title(x)
        self.tests = []
        for test in x.findall("//table[@id='suiteTable']//tr//a"):
            # Get HTML file for test
            x_test = etree.parse(test.get("href"), p)

            # Find test table
            test_title = _get_html_title(x_test)
            test_table = x_test.find("/body//table")

            if test_table != None:
                self.tests.append(SingleTest(test_title, test_table))
        os.chdir(old_dir)

class SingleStringAdaptor(SuiteAdaptor):
    ''' Creates a Test Suite with only one Test '''

    def __init__(self, name, data):
        self.name = name
        p = etree.HTMLParser()
        x = etree.parse(StringIO(data), p)
        test_title = _get_html_title(x)
        test_table = x.find("/body//table")
        self.tests = [SingleTest(test_title, test_table)]

class PySeleneseTestSuite(unittest.TestCase):
    ''' Creates a TestCase from a Selenese HTML suite '''

    def setUp(self):
        self.sel = selenium(
            self.server, self.port, self.driver, "http://%s/" % self.domain
        )
        self.sel.start()
        self.mapper = SeleniumMapper(self)

    def tearDown(self):
        self.sel.stop()

class PySeleneseError(Exception):
    """Subclass for PySelenese internal exceptions"""
    pass

def generate_test_case(adaptor, server="localhost", port=4444,
        driver="*firefox", domain="github.com", debug=False):
    ''' Returns a TestCase that runs all the tests found by the adaptor '''

    class TestCase(PySeleneseTestSuite): pass
    TestCase.server = server
    TestCase.port = port
    TestCase.driver = driver
    TestCase.domain = domain
    TestCase.debug = debug

    for i, table in enumerate(adaptor.get_tests()):
        fn = table.get_runnable()
        fn.__setattr__("__doc__", table.get_name())
        fn.__setattr__("_selenium_index", i)
        type(TestCase).__setattr__(TestCase, "test_%d" % i, fn)

    return TestCase

