'''
Although this looks an unittest module, it is not, as it doesn't test
the unittest_TAP. It is meant to be used only as an example of unittest_TAP use.
'''
import unittest_TAP


class Test(unittest_TAP.TestCase):
    def testRunningTest(self):
        """
        Empty test just to see that it is run.
        """
        self.assertTrue(True)

    @unittest_TAP.skip("demonstarting skipping")
    def testSkippingTest(self):
        """
        This test is to be skipped.
        """
        self.assertTrue(True)

    def testErrorTest(self):
        """
        This test ends in an error.
        """
        with self.assertRaises(IOError):
            raise ValueError

    def testFailedTest(self):
        """
        This test fails.
        """
        self.assertTrue(False)

    def testRunTestSuite(self):
        raise NotImplementedError("testRunTestSuite not implemented yet.")

if __name__ == "__main__":
    unittest_TAP.main()
