# -*- coding: utf-8 -*-
#Copyright (C) 2012 Red Hat, Inc.
#
#Permission is hereby granted, free of charge, to any person obtaining a copy of
#this software and associated documentation files (the "Software"), to deal in
#the Software without restriction, including without limitation the rights to
#use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
#of the Software, and to permit persons to whom the Software is furnished to do
#so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.
# Yes we want everything in this namespace!
try:
    from unittest2 import TestResult, TestCase, TestSuite, TextTestRunner, \
        TestLoader, FunctionTestCase, defaultTestLoader, SkipTest, \
        skip, skipIf, skipUnless, expectedFailure, TextTestResult, \
        __version__, collector, registerResult
    import unittest2 as unittest
except ImportError:
    from unittest import TestResult, TestCase, TestSuite, TextTestRunner, \
        TestLoader, FunctionTestCase, defaultTestLoader, SkipTest, \
        skip, skipIf, skipUnless, expectedFailure, TextTestResult, \
        registerResult
    import unittest

import tap
import logging

class TAPTestResult(TestResult):
    """A test result class that can print results to a stream as TAP stream.

    Used by TAPTestRunner.
    """
    def __init__(self, stream, descriptions, verbosity):
        TestResult.__init__(self)
        self.stream = stream
        self.errors = []
        self.writer = tap.TAPGenerator()
        self.showAll = verbosity > 1
        self.dots = verbosity == 1
        self.descriptions = descriptions

    def getDescription(self, test):
        doc_str = test._testMethodDoc
        doc_first_line = None
        if doc_str is not None:
            doc_first_line = [line.strip() for line in doc_str.split("\n")
                          if len(line.strip()) > 0]
        name = test._testMethodName
        if doc_first_line is not None:
            doc_first_line = doc_first_line[0]
        if self.descriptions and doc_first_line:
            return (name, doc_first_line)
        else:
            return (str(name), '')

    def startTest(self, test):
        TestResult.startTest(self, test)

    def addSuccess(self, test):
        TestResult.addSuccess(self, test)
        if self.showAll:
            name, desc = self.getDescription(test)
            self.stream.writeln(self.writer.format_TAP_msg(tap.PASS,
                name, desc))
        elif self.dots:
            self.stream.write('.')
            self.stream.flush()

    def addError(self, test, err):
        TestResult.addError(self, test, err)
        logging.debug("new error = %s", err)
        if self.showAll:
            name, desc = self.getDescription(test)
            self.stream.writeln(self.writer.format_TAP_msg(tap.ERROR,
                name, desc, self._exc_info_to_string(err, test)))
        elif self.dots:
            self.stream.write('E')
            self.stream.flush()

    def addFailure(self, test, err):
        TestResult.addFailure(self, test, err)
        if self.showAll:
            name, desc = self.getDescription(test)
            self.stream.writeln(self.writer.format_TAP_msg(tap.FAIL,
                name, desc))
        elif self.dots:
            self.stream.write('F')
            self.stream.flush()

    def addSkip(self, test, reason):
        TestResult.addSkip(self, test, reason)
        if self.showAll:
            name, desc = self.getDescription(test)
            self.stream.writeln(self.writer.format_TAP_msg(tap.SKIP,
                name, desc))
        elif self.dots:
            self.stream.write("s")
            self.stream.flush()

    def addExpectedFailure(self, test, err):
        TestResult.addExpectedFailure(self, test, err)
        if self.showAll:
            name, desc = self.getDescription(test)
            if desc:
                desc = "EXPECTED FAILURE " + desc
            else:
                desc = "EXPECTED FAILURE"
            self.stream.writeln(self.writer.format_TAP_msg(tap.PASS,
                                                           name, desc))
        elif self.dots:
            self.stream.write("x")
            self.stream.flush()

    def addUnexpectedSuccess(self, test):
        TestResult.addUnexpectedSuccess(self, test)
        if self.showAll:
            name, desc = self.getDescription(test)
            if desc:
                desc = "UNEXPECTED SUCCESS " + desc
            else:
                desc = "UNEXPECTED SUCCESS"
            self.stream.writeln(self.writer.format_TAP_msg(tap.FAIL, name, desc))
        elif self.dots:
            self.stream.write("u")
            self.stream.flush()

    def stopTestRun(self):
        TestResult.stopTestRun(self)
        if not self.showAll:
            self.stream.writeln()
            self.stream.flush()


class TAPTestRunner(TextTestRunner):
    def __init__(self, *args, **kwargs):  # IGNORE:W0622
        kwargs['resultclass'] = TAPTestResult
        TextTestRunner.__init__(self, *args, **kwargs)

    def run(self, test):
        "Run the given test case or test suite."
        result = self._makeResult()
        result.failfast = self.failfast
        result.buffer = self.buffer
        registerResult(result)

        startTestRun = getattr(result, 'startTestRun', None)
        if startTestRun is not None:
            startTestRun()
        try:
            test(result)
        finally:
            stopTestRun = getattr(result, 'stopTestRun', None)
            if stopTestRun is not None:
                stopTestRun()

        return result


class TAPTestProgram(unittest.TestProgram):
    def __init__(self, *kwds, **argkwds):
        unittest.TestProgram.__init__(self, *kwds, **argkwds)

def main():  # IGNORE:W0622 C0111
    TAPTestProgram(testRunner=TAPTestRunner)
