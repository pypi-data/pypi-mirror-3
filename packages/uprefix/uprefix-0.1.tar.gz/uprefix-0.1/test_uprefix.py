# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Vinay M. Sajip. See LICENSE for licensing information.
#
# Test harness for uprefix.
#

import logging
import os
import sys
import unittest

from uprefix import register_hook, unregister_hook

logger = logging.getLogger(__name__)

class UnicodePrefixRemover(unittest.TestCase):
    def setUp(self):
        register_hook()

    def tearDown(self):
        unregister_hook()

    def test_dummy(self):
        package_names = (
            'foo',
            'foo.level1', 'foo.bar',
            'foo.bar.level2', 'foo.bar.baz',
            'foo.bar.baz.level3',
        )
        for package_name in package_names:
            attr_name = package_name.replace('.', '_')
            # pass in __file__ so that the correct module is returned
            mod = __import__(package_name, fromlist=['__file__'])
            attr_value = getattr(mod, attr_name)
            self.assertEqual(attr_value, package_name)

if __name__ == '__main__':  #pragma: no cover
    # switch the level to DEBUG for in-depth logging.
    fn = 'test_uprefix-%d.%d.log' % sys.version_info[:2]
    logging.basicConfig(level=logging.DEBUG, filename=fn, filemode='w',
                        format='%(threadName)s %(funcName)s %(lineno)d '
                               '%(message)s')
    unittest.main()

