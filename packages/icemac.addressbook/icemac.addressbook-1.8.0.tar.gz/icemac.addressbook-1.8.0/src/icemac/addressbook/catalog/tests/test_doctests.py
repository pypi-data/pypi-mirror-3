# -*- coding: latin-1 -*-
# Copyright (c) 2008-2011 Michael Howitz
# See also LICENSE.txt
# $Id: test_doctests.py 1255 2011-03-05 08:25:37Z icemac $

import icemac.addressbook.testing


def test_suite():
    return icemac.addressbook.testing.FunctionalDocFileSuite(
        # Caution: none of these tests can run as unittest!
        'catalog.txt',
        package="icemac.addressbook.catalog",
        )
