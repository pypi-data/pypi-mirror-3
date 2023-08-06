import unittest, os
from load_tests import LoadTestCase
from find_tests import FindTestCase

if __name__ == '__main__':

	if not os.path.exists('speed_test_smaller.sql'):
		import speed_test
		speed_test.main()

	suite1 = unittest.TestLoader().loadTestsFromTestCase(LoadTestCase)
	suite2 = unittest.TestLoader().loadTestsFromTestCase(FindTestCase)
	unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([suite1, suite2]))

