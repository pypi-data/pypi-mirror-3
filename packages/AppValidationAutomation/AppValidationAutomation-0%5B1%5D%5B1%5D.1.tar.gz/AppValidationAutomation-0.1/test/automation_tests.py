#!/usr/bin/env python

from App.Validation.automation import *
from app_validation import AutoWrapper
import unittest, os, sys

class TestAutomation(unittest.TestCase, AutoWrapper):

    auto_obj = AutoWrapper()

    def setUp(self):
	TestAutomation.auto_obj.config['config_file'] = \
	                    os.path.abspath("./cfg/Conf.txt")
	TestAutomation.auto_obj.config['pass_phrase'] = '28bHIG82'

	self.config = TestAutomation.auto_obj.store_config()
        self.data   = {}

    def test_validate_urls(self):
        ret_value = \
            TestAutomation.auto_obj.validate_urls(['http://python.org'])

        self.assertEqual(ret_value, True)

    def test_check_dnsrr_lb(self):
        max_requests = int(1)
	min_unique   = int(1)
        ret_value =  TestAutomation.auto_obj.check_dnsrr_lb( \
	        'http://python.org', max_requests, min_unique) 

        self.assertEqual(ret_value, True)

    def test_validate_processes_mountpoints(self):
        ret_value = TestAutomation.auto_obj.validate_processes_mountpoints()

        self.assertEqual(ret_value, False)

if __name__ == '__main__':
    unittest.main()
