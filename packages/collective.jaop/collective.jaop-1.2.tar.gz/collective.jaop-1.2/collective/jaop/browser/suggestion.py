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
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import utils as cmfutils


class OpenSearchSuggestion(BrowserView):
    """ 
    A Browser view that returns XML instead of HTML.
    It also accesses preferences from the portal_preferences
    Tool. 
    """

    render = ViewPageTemplateFile('suggestion.pt')
    
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        self.request.response.setHeader('Content-Type', 'application/json')
        return self.render()

    def SearchSuggestions(self,busqueda):
        catalog = cmfutils.getToolByName(self.context, 'portal_catalog')
        kwargs = {}
        if ( busqueda == '*' ):
            busqueda = ''
        kwargs['SearchableText'] = busqueda
        search_results = catalog(**kwargs)
        return search_results  
              
