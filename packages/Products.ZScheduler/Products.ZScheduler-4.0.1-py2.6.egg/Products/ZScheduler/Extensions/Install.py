#    Copyright (C) 2005-2011  Corporation of Balclutha. All rights Reserved.
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
from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import getFSVersionTuple

from Products.ZScheduler.config import *


def install(portal):                                       
    out = StringIO()

    setup_tool = getToolByName(portal, 'portal_setup')

    if getFSVersionTuple()[0]>=3:
        setup_tool.runAllImportStepsFromProfile(
                "profile-ZScheduler:default",
                purge_old=False)
    else:
        plone_base_profileid = "profile-CMFPlone:plone"
        setup_tool.setImportContext(plone_base_profileid)
        setup_tool.setImportContext("profile-ZScheduler:default")
        setup_tool.runAllImportSteps(purge_old=False)
        setup_tool.setImportContext(plone_base_profileid)

    print >> out, "Successfully installed %s." % PROJECTNAME
    return out.getvalue()

def uninstall(portal, reinstall=False):
    out = StringIO()

    if not reinstall:
        setup_tool = getToolByName(portal, 'portal_setup')
        setup_tool.runAllImportStepsFromProfile('profile-ZScheduler:default')

    print >> out, "Successfully uninstalled %s." % PROJECTNAME
    return out.getvalue()


#
# it's a pain when this module won't load - this immediately lets us know !!!
#
if __name__ == '__main__':
    print 'brilliant - it compiles ...'
