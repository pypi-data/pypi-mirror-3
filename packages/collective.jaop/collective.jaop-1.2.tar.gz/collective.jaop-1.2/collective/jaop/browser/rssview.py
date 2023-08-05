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
from Products.CMFPlone.PloneBatch import Batch




class OpenSearchRssView(BrowserView):
    """ 
    A Browser view that returns rss2 for opensearch
    It also accesses preferences from the portal_preferences
    Tool. 
    """

    render = ViewPageTemplateFile('rssview.pt')
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.lenResult = 0
        self.pageSize = 3
        # Get the searchTerms from request
        if('search' in self.request.keys()):
            self.searchTerms = self.request['search']
        else:
            self.searchTerms = ''

        # Get the searchTerms from request
        if('startPage' in self.request.keys()):
            self.startPage = int(self.request['startPage'])
        else:
            self.startPage = 1
        self.startIndex = 3*(self.startPage-1)+1

    def __call__(self):
        self.request.response.setHeader('Content-Type', 'application/xml')
        self.request.response.setHeader('charset','utf-8')
        return self.render()

    def Search(self):
        catalog = cmfutils.getToolByName(self.context, 'portal_catalog')
        kwargs = {}
        if ( self.searchTerms == '*' ):
            self.searchTerms = ''
        kwargs['SearchableText'] = self.searchTerms
        search_results = catalog(**kwargs)
        self.lenResult = len(search_results)
        if ( (self.startPage-1) * self.pageSize > self.lenResult ):
            back = []
        else:
            back = Batch(search_results,self.pageSize,self.pageSize*(self.startPage-1),orphan=1)
        return back
