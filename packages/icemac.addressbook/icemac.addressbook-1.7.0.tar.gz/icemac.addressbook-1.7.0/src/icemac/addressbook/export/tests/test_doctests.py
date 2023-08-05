# -*- coding: latin-1 -*-
# Copyright (c) 2008-2011 Michael Howitz
# See also LICENSE.txt
# $Id: test_doctests.py 1369 2011-11-03 19:20:18Z icemac $
import icemac.addressbook.testing


def test_suite():
    return icemac.addressbook.testing.FunctionalDocFileSuite(
        'export.txt',
        'sortorder.txt',
        'userfields.txt',
        package='icemac.addressbook.export',
        )
