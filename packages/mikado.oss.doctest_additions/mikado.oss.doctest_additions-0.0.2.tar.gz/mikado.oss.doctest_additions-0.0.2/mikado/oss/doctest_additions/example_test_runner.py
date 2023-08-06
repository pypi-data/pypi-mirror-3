#!/usr/local/bin/python



import unittest
import doctest
import sys
import xmlrunner
from optparse import OptionParser

from mikado.oss import doctest_additions

"""
An example of a test runner *script*

It is designed to solely run one or more text files that hold one or more valid doctests.
It is expected to be included in your package structure in test-driectory::

  myapp/
   setup.py
   docs/
   myapp/
     myapp.py
     tests/
        mytestrunner.py
        mytests.txt

When run without arguments, this example file will execute the doctests as "normal"
except it will substitute doctest_additions.testfile for the official testfile

This at the moment means all runs as usual, unless output lines begin "[logline]"
when those lines will be ignored when comparing expected and got output for each TestCase.

If called with "jenkins" as sole argument, then the example will do exactly the same 
but will output xunit formatted XML into directory "testresults"


example usage::

    doctest_additions.testfile("tests.txt", 
                            checker=doctest_additions.MyOutputChecker())


useage::

   example_test_runner.py test.txt 

     will produce usual doctest results

   example_test_runner.py test.txt test2.txt --jenkins

     will output the results of two suites, as XML
   

"""


def test_doctest(f):
    doctest_additions.testfile(f, checker=doctest_additions.MyOutputChecker())

def asunittest(f):

   tsuite = doctest.DocFileSuite(f, checker=doctest_additions.MyOutputChecker())
   xmlrunner.XMLTestRunner(output="testresults").run(tsuite)




class doctest_additionsError(Exception):
    pass

def parse_args():

    parser = OptionParser()
    parser.add_option("--jenkins", dest="jenkins", action="store_true", default=False,
                      help="If set, output results as xunit XML to testresults folder")
    (options, args) = parser.parse_args()
    return (options, args)

def main():
    options, args = parse_args()
    if args == []:
        raise doctest_additionsError("You must supply at least one path to a valid doctest example file")

    for testfile in args:
       
        if options.jenkins==True:
            asunittest(testfile)
        else:
            test_doctest(testfile)
  

if __name__ == '__main__':
    main()



