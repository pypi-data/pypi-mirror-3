# -*- coding: latin-1 -*-
# Copyright (c) 2008-2011 Michael Howitz
# See also LICENSE.txt
# $Id: evolve17.py 1258 2011-03-10 20:28:56Z icemac $

import icemac.addressbook.generations.utils


def evolve(context):
    """Install `name` index.
    """
    icemac.addressbook.generations.utils.update_address_book_infrastructure(
        context)
