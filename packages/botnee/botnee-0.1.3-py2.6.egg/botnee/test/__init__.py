#!/usr/bin/env python
"""
Unit testing sub-package
This file provides a simple test harness which is called
for all of the methods of the modules in the super-package.
"""
import sys

#from botnee import *
__all__ = ["test_corpus", "test_process", "test_standard_document_io", "test_json_io"]

import test_corpus
import test_process
import test_standard_document_io
import test_json_io

def test_harness(name, test_data):
    if len(name) == 2:
        function = "test_" + name[0] + ".test_" + name[1]
    else:
        function = name
    sys.stdout.write("Testing " + function + "()...")
    (result, test_data) = eval(function + "(test_data)")
    if result:
        sys.stdout.write("success\n")
    else:
        sys.stdout.write("failed\n")
    return (result, test_data)

