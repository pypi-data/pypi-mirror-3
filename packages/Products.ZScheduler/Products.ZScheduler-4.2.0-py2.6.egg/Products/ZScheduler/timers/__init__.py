#    Copyright (C) 2004-2009 Corporation of Balclutha. All rights Reserved.
#
#    For your open source solution, bureau service and consultancy requirements,
#    visit us at http://www.balclutha.org or http://www.last-bastion.net.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
from Products.CMFCore.utils import registerIcon

import os, os.path
directory = os.path.dirname(__file__)

_timers = filter( lambda x: os.path.isdir(os.path.join(directory, x)) and x not in ['.svn', 'CVS'],
                  os.listdir(directory) )

__all__ = _timers

# make a copy ...
def timers() : return list(_timers)

from AccessControl import ModuleSecurityInfo
ModuleSecurityInfo('Products').declarePublic('ZScheduler')
ModuleSecurityInfo('Products.ZScheduler').declarePublic('timers')
ModuleSecurityInfo('Products.ZScheduler.timers').declarePublic('timers')

def initialize(context):
    for provider in timers():
        exec('''registerIcon(%s.%s, 'times/%s/www/%s.gif', globals())''' % (provider, 
                                                                            provider, 
                                                                            provider.lower()))


