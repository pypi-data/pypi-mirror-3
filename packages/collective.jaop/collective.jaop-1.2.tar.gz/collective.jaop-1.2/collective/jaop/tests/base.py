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

__author__ = 'Brent Lambert, David Ray, Jon Thomas'
__docformat__ = 'restructuredtext'
__version__ = "$Revision: 1 $"[11:-2]

from zope.testing import doctest
from zope.testing.doctestunit import DocFileSuite
from Testing import ZopeTestCase
from Testing.ZopeTestCase import FunctionalDocFileSuite, ZopeDocFileSuite, Functional
from Testing.ZopeTestCase import ZopeDocFileSuite
from Products.PloneTestCase.PloneTestCase import PloneTestCase
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase, setupPloneSite, installProduct, installPackage
from setuptools import find_packages

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase.layer import onsetup
from Testing import ZopeTestCase as ztc
from Products.CMFPlone.tests import dummy


@onsetup
def setup_jaop_project():
    """Set up the additional products required for the  tests.
    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """
    # Load the ZCML configuration for the collective.jaop package
    fiveconfigure.debug_mode = True

    import collective.jaop
    zcml.load_config('configure.zcml', collective.jaop)
    fiveconfigure.debug_mode = False
    
    ztc.installPackage('collective.jaop')

setup_jaop_project()
setupPloneSite(with_default_memberarea=0, extension_profiles=['collective.jaop:default',])           

oflags = (doctest.ELLIPSIS |
          doctest.NORMALIZE_WHITESPACE)
prod = 'collective.jaop'

class jaopTestCase(PloneTestCase):
    """ Unit test package for jaopTestCase"""

class jaopFunctionalTestCase(Functional, jaopTestCase):
    """ Base class for functional integration tests. """


