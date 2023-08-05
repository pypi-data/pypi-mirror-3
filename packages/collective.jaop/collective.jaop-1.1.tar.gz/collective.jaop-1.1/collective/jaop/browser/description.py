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

from zope.publisher.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class OpenSearchDescription(BrowserView):
    """ 
    A Browser view that returns XML instead of HTML.
    It also accesses preferences from the portal_preferences
    Tool. 
    """

    render = ViewPageTemplateFile('description.pt')
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        props = getToolByName(context, 'portal_properties', None)
        if props:
            self.osprops = props.opensearch_properties
        else:
            self.osprops = None

    def __call__(self):
        self.request.response.setHeader('Content-Type', 'application/xml')
        return self.render()

    def getTheDescription(self):
        return self.osprops.description

    def getTags(self):
        return self.osprops.tags
        
    def getContact(self):
        return self.osprops.contact
        
    def getTitle(self):
        return self.osprops.shortName
        
    def getAllowHTML(self):
        return self.osprops.allowXHTML

    def getAllowRSS(self):
        return self.osprops.allowRSS                                
       
    def getAllowAtom(self):
        return self.osprops.allowAtom                
