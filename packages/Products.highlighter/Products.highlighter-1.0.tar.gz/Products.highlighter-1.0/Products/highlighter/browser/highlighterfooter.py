# -*- coding: us-ascii -*-
# _______________________________________________________________________________
#
#  Copyright (c) 2011 Highlighter, All rights reserved.
# _______________________________________________________________________________
#                                                                                 
#  This program is free software; you can redistribute it and/or modify         
#  it under the terms of the GNU General Public License as published by         
#  the Free Software Foundation, version 2.                                     
#                                                                                 
#  This program is distributed in the hope that it will be useful,             
#  but WITHOUT ANY WARRANTY; without even the implied warranty of               
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               
#  GNU General Public License for more details.                                 
#                                                                                 
#  You should have received a copy of the GNU General Public License           
#  along with this program; if not, write to the Free Software                 
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   
# _______________________________________________________________________________

__author__ = 'Brent Lambert <brent@enpraxis.net>'


from plone.app.layout.viewlets.common import ViewletBase
from zope.app.component.hooks import getSite


highlighter_script = """var _hl=_hl||{};_hl.site='%s';(function(){var hl=document.createElement('script');hl.type='text/javascript';hl.async=true;hl.src=document.location.protocol+'//highlighter.com/webscript/v1/js/highlighter.js';var s=document.getElementsByTagName('script')[0];s.parentNode.insertBefore(hl,s);})();"""


class HighlighterFooter(ViewletBase):
    """ Highlighter script viewlet """

    def __init__(self, context, request, view, manager=None):
        super(HighlighterFooter, self).__init__(context, request, view, manager)
        site = getSite()
        self.hp = site.portal_properties.highlighter_properties

    def isShowable(self):
        """ Is Highlighter integration enabled """
        return self.hp.getProperty('enable')

    def getScript(self):
        """ Get Highlighter script """
        hid = self.hp.getProperty('highlighterId')
        if hid:
            script = highlighter_script % hid
            return script
        return ''
