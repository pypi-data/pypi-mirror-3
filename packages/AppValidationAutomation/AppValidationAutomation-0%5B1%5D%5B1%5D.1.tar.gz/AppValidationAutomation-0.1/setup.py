#!/usr/bin/env python

from distutils.core import setup

setup(
    name          = 'AppValidationAutomation',
    version       = '0.1',
    description   = 'Automation Framework - Web and Unix Centric Apps',
    author        = 'Varun Juyal',
    author_email  = 'varunjuyal123@yahoo.com',
    url           =
                      'http://pypi.python.org/pypi/AppValidationAutomation/0.1',
    py_modules    = ['App.Validation.automation', 
                     'App.Validation.Automation.web', 
                     'App.Validation.Automation.unix', 
                     'App.Validation.Automation.alarming', 
                     'App.Validation.Automation.purging'],
    provides      = ['automation (0.1)'],
    requires      = ['doctest', 'os', 'ssh', 're', 'types', 'getopt',
                     'socket', 'smtplib', 'logging', 'glob', 'time', 'string', 'sys',
                     'profile', 'datetime', 'ConfigParser', 'unittest',
                     'pyDes (>=2.0.0)', 'mechanize (>=0.2.5)'],
    scripts       = ['bin/app_validation.py'],
    data_files    = [('data', ['pass.txt']),
                     ('docs', []),
		     ('test', ['automation_tests.py']),
		     ('cfg', ['Conf.txt']),
		     ('log', [])]
)

