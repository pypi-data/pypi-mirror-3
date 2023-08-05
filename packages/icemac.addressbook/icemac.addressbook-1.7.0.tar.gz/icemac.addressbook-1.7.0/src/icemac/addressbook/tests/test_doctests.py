# -*- coding: latin-1 -*-
# Copyright (c) 2008-2011 Michael Howitz
# See also LICENSE.txt
# $Id: test_doctests.py 1370 2011-11-03 19:36:53Z icemac $

import icemac.addressbook.testing
import unittest


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(icemac.addressbook.testing.FunctionalDocFileSuite(
        # Caution: none of these tests can run as unittest!
        'adapter.txt',
        'address.txt',
        'addressbook.txt',
        'person.txt',
        ))
    suite.addTest(icemac.addressbook.testing.TestBrowserDocFileSuite(
        'testing.txt',
        ))
    return suite
