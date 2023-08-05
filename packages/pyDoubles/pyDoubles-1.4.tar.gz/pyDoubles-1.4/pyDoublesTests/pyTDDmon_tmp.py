import unittest

suite = unittest.TestSuite()
load_module_tests = unittest.defaultTestLoader.loadTestsFromModule

import unit
suite.addTests(load_module_tests(unit))

if __name__ == '__main__':
	unittest.TextTestRunner().run(suite)
