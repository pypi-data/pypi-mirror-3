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


from zope.i18nmessageid import MessageFactory


def initialize(context):
    """Initializer called when used as a Zope 2 product."""


HighlighterMessageFactory = MessageFactory('Highlighter')
