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


from zope.publisher.browser import BrowserView
from zope.app.component.hooks import getSite
from urlparse import urlparse, urlunparse

class HighlighterEnableMessage(BrowserView):
    """ Add message to enable widget if Highlighter integratoin is not enabled. """

    def isEnabled(self):
        """ Is highlighter enabled """
        site = getSite()
        hp = site.portal_properties.highlighter_properties
        return hp.getProperty('enable')

    def getSiteName(self):
        """ Get site name for use in Highlighter account """
        site = getSite()
        purl = site.absolute_url()
        parts = urlparse(purl)
        purl = urlunparse((parts.scheme, parts.hostname, '', '', '', '',))
        return purl
        
