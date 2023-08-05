# Copyright (c) 2008-2011 Michael Howitz
# See also LICENSE.txt
# $Id: __init__.py 1417 2011-12-03 19:32:58Z icemac $
"""Database initialisation and upgrading."""

import zope.generations.generations


GENERATION = 18


manager = zope.generations.generations.SchemaManager(
    minimum_generation=GENERATION,
    generation=GENERATION,
    package_name='icemac.addressbook.generations')
