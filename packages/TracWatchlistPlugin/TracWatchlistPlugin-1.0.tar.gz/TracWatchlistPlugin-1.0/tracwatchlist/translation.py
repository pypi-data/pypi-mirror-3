# -*- coding: utf-8 -*-
"""
= Watchlist Plugin for Trac =
Plugin Website:  http://trac-hacks.org/wiki/WatchlistPlugin
Trac website:    http://trac.edgewall.org/

Copyright (c) 2008-2010 by Martin Scharrer <martin@scharrer-online.de>
All rights reserved.

The i18n support was added by Steffen Hoffmann <hoff.st@web.de>.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

For a copy of the GNU General Public License see
<http://www.gnu.org/licenses/>.

$Id: translation.py 11371 2012-03-10 20:27:00Z martin_s $
"""

__url__      = ur"$URL: http://trac-hacks.org/svn/watchlistplugin/0.12/tracwatchlist/translation.py $"[6:-2]
__author__   = ur"$Author: martin_s $"[9:-2]
__revision__ = int("0" + ur"$Rev: 11371 $"[6:-2].strip('M'))
__date__     = ur"$Date: 2012-03-10 21:27:00 +0100 (Sat, 10 Mar 2012) $"[7:-2]

# Import translation functions. Fallbacks are provided for Trac 0.11.
try:
    from  trac.util.translation  import  domain_functions
    add_domain, _, N_, tag_, gettext, ngettext = \
        domain_functions('watchlist', ('add_domain', '_', 'N_', 'tag_', 'gettext', 'ngettext'))
    i18n_enabled = True
except ImportError:
    from  trac.util.translation  import  gettext, ngettext
    _, N_, tag_  = gettext, gettext, None
    def add_domain(a,b,c=None):
        pass
    i18n_enabled = False

# Import tracs `N_` as `T_` to mark strings already translated by trac.
# Note: Later this might also be needed for `_`.
try:
    from  trac.util.translation  import  N_ as T_
    from  trac.util.translation  import   _ as t_
except:
    T_ = N_
    t_ =  _

# EOF
