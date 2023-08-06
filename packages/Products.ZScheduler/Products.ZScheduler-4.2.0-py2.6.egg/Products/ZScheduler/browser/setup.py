#
# Copyright 2012 Corporation of Balclutha (http://www.balclutha.org)
# 
#                All Rights Reserved
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
#
# Corporation of Balclutha DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS, IN NO EVENT SHALL Corporation of Balclutha BE LIABLE FOR
# ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE. 
#
from Acquisition import aq_base, aq_inner
from Products.Five.browser import BrowserView

from Products.ZScheduler.ZScheduler import ZScheduler



class ZSchedulerTool(BrowserView):
    """
    Creates a Zenoss installation
    """

    def createTool(self):
        """
        creates zport, DMD in install root
        """
        context = aq_inner(self.context)

	context._setObject('ZSchedulerTool', ZScheduler())	

        self.request.set('manage_tabs_message', 'created ZSchedulerTool')
        self.request.RESPONSE.redirect('/manage_main')

