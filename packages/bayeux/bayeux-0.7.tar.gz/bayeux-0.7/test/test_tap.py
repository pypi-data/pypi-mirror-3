'''
Created on 22.3.2012

@author: matej
'''
import sys
try:
    import unittest2 as unittest
except ImportError:
    import unittest
import tap
import logging
import subprocess
import os.path

class Test(unittest.TestCase):
    def test_simple_statement(self):
        name = "simple pass statement"
        result = tap.PASS
        expected = "ok - %s" % name
        observed = tap.TAPGenerator().format_TAP_msg(result, name)
        self.assertEqual(expected, observed)

    def test_skip_statement(self):
        name = "simple skip statement"
        result = tap.SKIP
        expected = "ok - %s\t# %s " % (name, "SKIP")
        observed = tap.TAPGenerator().format_TAP_msg(result, name)
        self.assertEqual(expected, observed)

    def test_fail_statement(self):
        name = "simple fail statement"
        result = tap.FAIL
        expected = "not ok - %s\t# %s " % (name, "FAIL")
        observed = tap.TAPGenerator().format_TAP_msg(result, name)
        self.assertEqual(expected, observed)

    def test_error_statement(self):
        name = "simple error statement"
        result = tap.ERROR
        expected = "not ok - %s\t# %s " % (name, "ERROR")
        observed = tap.TAPGenerator().format_TAP_msg(result, name)
        self.assertEqual(expected, observed)

    def test_statement_with_data(self):
        name = "complex statement with data"
        result = tap.PASS
        expected = "ok - %s\n  ---\n  justification: |-\n" % name \
            + "    very hungry\n    dog ate my homework\n  reason: 42\n  ..."
        observed = tap.TAPGenerator().format_TAP_msg(result, name, None, {
           "reason": 42,
           "justification": "very hungry\ndog ate my homework"
        })
        self.assertEqual(expected, observed)

    @unittest.skipIf(sys.version_info > (2 , 6), ">= 2.7 has incompatible repr() for floats.")
    def test_generate_TAP(self):
        logging.debug("current directory = %s" % os.path.realpath(os.path.curdir))
        cmd = subprocess.Popen(['python', 'generate_TAP', './test/data/results.json'],
                   bufsize= -1, close_fds=True, stdout=subprocess.PIPE)
        (stdoutdata, _) = cmd.communicate()
        if(cmd.returncode == 0):
            exp_file = open("test/data/results.tap", "r")
            expected = exp_file.read()
            self.assertEqual(expected, stdoutdata, "generated TAP from JSON piglit results.")



if __name__ == "__main__":
    unittest.main()
