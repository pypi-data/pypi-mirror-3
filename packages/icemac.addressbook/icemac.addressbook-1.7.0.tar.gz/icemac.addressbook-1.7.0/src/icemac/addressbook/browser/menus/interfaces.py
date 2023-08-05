# -*- coding: latin-1 -*-
# Copyright (c) 2008-2011 Michael Howitz
# See also LICENSE.txt
# $Id: interfaces.py 1229 2011-01-29 17:07:16Z icemac $

import z3c.menu.ready2go


class IMainMenu(z3c.menu.ready2go.ISiteMenu):
    """Main menu."""


class IAddMenu(z3c.menu.ready2go.IAddMenu):
    """Add menu."""
