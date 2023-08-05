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
from base import jaopTestCase
from Products.CMFCore.utils import getToolByName

class testInstall(jaopTestCase):

    def test_jaopInstall(self):
        self.failUnless('collective.jaop' in [product['product'] for product in self.portal.portal_setup.listProfileInfo()])
        
    def test_installControlPanel(self):
        control_panel = getToolByName(self.portal, 'portal_controlpanel', None)
        self.failUnless('OpenSearch' in [listAction.id for listAction in control_panel.listActions()])        

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testInstall))
    return suite


