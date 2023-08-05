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


from zope.interface import Interface, implements
from zope.component import adapts, getUtility
from zope.formlib.form import FormFields, action
from zope.schema import Bool, Text, TextLine
from Products.highlighter import HighlighterMessageFactory as _
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFCore.interfaces import IPropertiesTool
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from plone.app.controlpanel.form import ControlPanelForm
from plone.fieldsets.fieldsets import FormFieldsets
from zope.app.form.browser.widget import SimpleInputWidget
from plone.app.form.widgets import CheckBoxWidget
from zope.app.component.hooks import getSite
from urllib2 import urlopen, quote
from urlparse import urlparse, urlunparse
import re


hurl = 'http://highlighter.com/wordpress_plugin_remote.php?site_url='


class HighlighterEnableWidget(CheckBoxWidget):
    """ Custom check box widget with additional information """

    def __call__(self):
        site = getSite()
        result = super(HighlighterEnableWidget, self).__call__()
        template = site.restrictedTraverse('@@highlighter-enablemessage')
        result += template()
        return result
        

class HighlighterManagementWidget(SimpleInputWidget):
    """ Display widget for Analytics """

    def __call__(self):
        site = getSite()
        template = site.restrictedTraverse('@@highlighter-management')
        return template()
 

class HighlighterAnalyticsWidget(SimpleInputWidget):
    """ Display widget for Analytics """

    def __call__(self):
        site = getSite()
        template = site.restrictedTraverse('@@highlighter-analytics')
        return template()
    

class IHighlighterControlPanelSettings(Interface):
    """ Control Panel Settings Tab """

    enable = Bool(title=_(u'Enable'),
                  description=_(u'Enable highlighter functionality.'),
                  default=False)


class IHighlighterControlPanelManagement(Interface):
    """ Control Panel Analytics Tab """

    management = Text(title=_(u'Management'),
                      description=_(u''),
                      readonly=False,
                      default=u'')


class IHighlighterControlPanelAnalytics(Interface):
    """ Control Panel Analytics Tab """

    analytics = Text(title=_(u'Analytics'),
                     description=_(u''),
                     readonly=False,
                     default=u'')



class IHighlighterControlPanelCombined(IHighlighterControlPanelSettings, 
                                       IHighlighterControlPanelManagement,
                                       IHighlighterControlPanelAnalytics):
    """ Combined setttings for Highlighter ControlPanel """

    
class HighlighterControlPanelAdapter(SchemaAdapterBase):
    """ Highlighter Control Panel Adapter - adapts form to property sheet """

    adapts(IPloneSiteRoot)
    implements(IHighlighterControlPanelCombined)

    def __init__(self, context):
        super(HighlighterControlPanelAdapter, self).__init__(context)
        self.props = getUtility(IPropertiesTool)
        self.hp = self.props.highlighter_properties
        self.cssreg = getToolByName(self.context, 'portal_css')

    def get_enable(self):
        return self.hp.getProperty('enable')

    def set_enable(self, value):
        return
#        hid = ''
#        if value:
#            site = getSite()
#            purl = site.absolute_url()
#            parts = urlparse(purl)
#            purl = urlunparse((parts.scheme, parts.hostname, '', '', '', '',))
#            hl = urlopen(hurl + quote(purl) + '/')
#            if hl:
#                result = hl.read()
#                hl.close()
#            else:
#                result = ''
#            value = re.compile(r'(\d*)')
#            mo = value.match(result)
#            if mo:
#                hid = result[mo.start():mo.end()]
#        if hid:
#            self.hp.manage_changeProperties(enable=True, highlighterId=hid)
#            self.cssreg.updateStylesheet(id='++resource++highlighter.css', 
#                                         enabled=1)
#        else:
#            self.hp.manage_changeProperties(enable=False, highlighterId='')
#            self.cssreg.updateStylesheet(id='++resource++highlighter.css', 
#                                         enabled=0)

    def get_management(self):
        return ''

    def set_management(self, dummy):
        return

    def get_analytics(self):
        return ''

    def set_analytics(self, dummy):
        return

    enable = property(get_enable, set_enable)
    management = property(get_management, set_management)
    analytics = property(get_analytics, set_analytics)
    


settingsset = FormFieldsets(IHighlighterControlPanelSettings)
settingsset.id = 'highlightersettings'
settingsset.label = _(u'Settings')

managementset = FormFieldsets(IHighlighterControlPanelManagement)
managementset.id = 'highlightermanagement'
managementset.label = _(u'Management')

analyticsset = FormFieldsets(IHighlighterControlPanelAnalytics)
analyticsset.id = 'highlighteranalytics'
analyticsset.label = _(u'Analytics')


class HighlighterControlPanel(ControlPanelForm):
    """ Highlighter Control Panel Form """

    form_fields = FormFieldsets(settingsset, managementset, analyticsset)
    form_fields['enable'].custom_widget = HighlighterEnableWidget
    form_fields['management'].custom_widget = HighlighterManagementWidget
    form_fields['analytics'].custom_widget = HighlighterAnalyticsWidget
    
    label = _(u'Highlighter Integration')
    description = _(u'')
    form_name = _(u'Highlihter Settings')


    @action(_(u'Save'), name='save')
    def handle_save(self, action, data):
        """ Enable Highlighter integration """
        props = getUtility(IPropertiesTool)
        hp = props.highlighter_properties
        cssreg = getToolByName(self.context, 'portal_css')
        hid = ''
        if data['enable']:
            site = getSite()
            purl = site.absolute_url()
            parts = urlparse(purl)
            purl = urlunparse((parts.scheme, parts.hostname, '', '', '', '',))
            hl = urlopen(hurl + quote(purl) + '/')
            if hl:
                result = hl.read()
                hl.close()
            else:
                result = ''
            value = re.compile(r'(\d*)')
            mo = value.match(result)
            if mo:
                hid = result[mo.start():mo.end()]
        if hid:
            hp.manage_changeProperties(enable=True, highlighterId=hid)
            cssreg.updateStylesheet(id='++resource++highlighter.css', 
                                    enabled=1)
            self.status = _(u'text_highlighter_enabled', default=u'Highlighter functionality enabled.')
            return
        else:
            hp.manage_changeProperties(enable=False, highlighterId='')
            cssreg.updateStylesheet(id='++resource++highlighter.css', 
                                    enabled=0)
            if data['enable']:
                self.status = _(u'text_highlighter_not_enabled', 
                                default=u'Highlighter integration could not be completed. Please check your Highlighter account settings.')
                return


    
