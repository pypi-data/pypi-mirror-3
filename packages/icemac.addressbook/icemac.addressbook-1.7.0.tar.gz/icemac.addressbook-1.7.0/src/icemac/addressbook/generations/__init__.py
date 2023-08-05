# Copyright (c) 2008-2011 Michael Howitz
# See also LICENSE.txt
# $Id: __init__.py 1258 2011-03-10 20:28:56Z icemac $
"""Database initialisation and upgrading."""

import zope.generations.generations


GENERATION = 17


manager = zope.generations.generations.SchemaManager(
    minimum_generation=GENERATION,
    generation=GENERATION,
    package_name='icemac.addressbook.generations')
