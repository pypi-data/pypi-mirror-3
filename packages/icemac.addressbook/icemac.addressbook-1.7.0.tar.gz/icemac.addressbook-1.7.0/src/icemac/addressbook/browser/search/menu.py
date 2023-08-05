# -*- coding: latin-1 -*-
# Copyright (c) 2008-2011 Michael Howitz
# See also LICENSE.txt
# $Id: menu.py 1229 2011-01-29 17:07:16Z icemac $

import zope.viewlet.manager
import z3c.menu.ready2go
import z3c.menu.ready2go.manager


SearchMenu = zope.viewlet.manager.ViewletManager(
    'left', z3c.menu.ready2go.IContextMenu,
    bases=(z3c.menu.ready2go.manager.MenuManager,))
