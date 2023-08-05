##################################################################################
#    Copyright (c) 2009 Massachusetts Institute of Technology, All rights reserved.
#                                                                                 
#    This program is free software; you can redistribute it and/or modify         
#    it under the terms of the GNU General Public License as published by         
#    the Free Software Foundation, version 2.                                      
#                                                                                 
#    This program is distributed in the hope that it will be useful,              
#    but WITHOUT ANY WARRANTY; without even the implied warranty of               
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                
#    GNU General Public License for more details.                                 
#                                                                                 
#    You should have received a copy of the GNU General Public License            
#    along with this program; if not, write to the Free Software                  
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA                                                                  
##################################################################################

from zope.interface import Interface, implements
from zope.component import adapts, getUtility
from zope.formlib.form import FormFields
from zope.schema import TextLine, Text, Bool
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.interfaces import IPropertiesTool
from plone.app.controlpanel.form import ControlPanelForm
from collective.jaop import OpenSearchMessageFactory as _

class IOpenSearchSettingsForm(Interface):
    """ The view interface for the open search prefs form """

    shortName = TextLine(title=_(u'Title'),
                         description=_(u'A short name for your Open Search widget. Limited to 16 characters'),
                         max_length=16)

    description = Text(title=_(u'Description'),
                           description=_(u'A human-readable description of the'
                                         'search engine. Limited to 1024 characters'),
                           max_length=1024)

    tags = Text(title=_(u'Tags'),
                description=_(u'Tags, one per line.'),
                required=False)

    contact = TextLine(title=_(u'Contact'),
                       description=_(u'An email address of someone to contact.'),
                       required=False)

    allowRSS = Bool(title=_(u'Allow OpenSearch via RSS'),
                    description=_(u'Allow OpenSearch via RSS'),
                    required=False)

#    allowAtom = Bool(title=_(u'Allow OpenSearch via Atom'),
#                     description=_(u'Allow OpenSearch via Atom'),
#                     required=False)

    allowXHTML = Bool(title=_(u'Allow OpenSearch via XHTML + xml'),
                      description=_(u'Allow OpenSearch via XHTML + xml'),
                      required=False)
                     

class OpenSearchControlPanelAdapter(SchemaAdapterBase):
    """ 
    Adapter that adapts the control panel form values to portal_properties. 
    """

    adapts(IPloneSiteRoot)
    implements(IOpenSearchSettingsForm)

    def __init__(self, context):
        super(OpenSearchControlPanelAdapter, self).__init__(context)
        pt = getUtility(IPropertiesTool)
        self.osprops = pt.opensearch_properties

    def get_shortName(self):
        return self.osprops.shortName

    def set_shortName(self, name):
        self.osprops.shortName = name

    def get_description(self):
        return self.osprops.description

    def set_description(self, desc):
        self.osprops.description = desc

    def get_tags(self):
        return self.osprops.tags

    def set_tags(self, tags):
        self.osprops.tags = tags

    def get_contact(self):
        return self.osprops.contact

    def set_contact(self, contact):
        self.osprops.contact = contact

    def get_allowRSS(self):
        return self.osprops.allowRSS

    def set_allowRSS(self, allow):
        self.osprops.allowRSS = allow

#    def get_allowAtom(self):
#        return self.osprops.allowAtom 

#    def set_allowAtom(self, allow):
#        self.osprops.allowAtom = allow

    def get_allowXHTML(self):
        return self.osprops.allowXHTML

    def set_allowXHTML(self, allow):
        self.osprops.allowXHTML

    shortName = property(get_shortName, set_shortName)
    description = property(get_description, set_description)
    tags = property(get_tags, set_tags)
    contact = property(get_contact, set_contact)
    allowRSS = property(get_allowRSS, set_allowRSS)
#    allowAtom = property(get_allowAtom, set_allowAtom)
    allowXHTML = property(get_allowXHTML, set_allowXHTML)

class OpenSearchPrefsForm(ControlPanelForm):
    """ The preferences form. """
    implements(IOpenSearchSettingsForm)
    form_fields = FormFields(FormFields(IOpenSearchSettingsForm))

    label = _(u'Open Search Settings Form')
    description = _(u'stuff')
    form_name = _(u'OpenSearch Settings')


                           

