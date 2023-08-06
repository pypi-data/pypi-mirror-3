#!/usr/bin/env python

import sys
import unittest

from pyselenese2 import generate_test_case, TestSuiteFileAdaptor, SingleStringAdaptor

try:
    server = sys.argv[1]
    sys.argv.pop(1)
except IndexError:
    server = "localhost"

# Test loading a test case from a string
StringTest = generate_test_case(
    SingleStringAdaptor('test_string',
        open('test_input_files/test-a.html').read()),
    server
)

# Test basic multi-file tests
BasicTests = generate_test_case(
    TestSuiteFileAdaptor("test_input_files"),
    server
)

# Also test more than one class
SecondTest = generate_test_case(
    TestSuiteFileAdaptor("test_input_files/secondtest"),
    server
)

# Test supported actions
ActionsTests = generate_test_case(
    TestSuiteFileAdaptor("test_input_files/actions"),
    server
)

unittest.main()
