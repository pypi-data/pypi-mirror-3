"""
Simple test harness function
"""

import sys

#from botnee import test

def test_harness(function, test_data):
    """
    Returns the result of the test along with the test_data object updated
    """
    name = "test.test_" + function[0] + '.test_' + function[1]
    
    sys.stdout.write("Testing " + name + "()...")
    (result, test_data) = eval(name + "(test_data)")
    if result:
        sys.stdout.write("success\n")
    else:
        sys.stdout.write("failed\n")
    return (result, test_data)

