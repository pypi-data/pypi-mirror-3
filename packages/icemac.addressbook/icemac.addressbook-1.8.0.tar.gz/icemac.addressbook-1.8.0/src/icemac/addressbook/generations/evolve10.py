# -*- coding: latin-1 -*-
# Copyright (c) 2008-2011 Michael Howitz
# See also LICENSE.txt
# $Id: evolve10.py 1229 2011-01-29 17:07:16Z icemac $

import icemac.addressbook.generations.utils


def evolve(context):
    """Install default preferences provider.
    """
    icemac.addressbook.generations.utils.update_address_book_infrastructure(
        context)
