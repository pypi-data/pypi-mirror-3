##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Setting up an environment for testing context-dependent objects

$Id: setup.py 110724 2010-04-11 00:04:11Z tseaver $
"""
import zope.component
import zope.traversing.api

#------------------------------------------------------------------------
# Annotations
from zope.annotation.attribute import AttributeAnnotations
def setUpAnnotations():
    zope.component.provideAdapter(AttributeAnnotations)

#------------------------------------------------------------------------
# Dependencies
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.app.dependable import Dependable
from zope.app.dependable.interfaces import IDependable
def setUpDependable():
    zope.component.provideAdapter(Dependable, (IAttributeAnnotatable,),
                                  IDependable)

#------------------------------------------------------------------------
# Traversal
from zope.traversing.interfaces import ITraversable
from zope.container.interfaces import ISimpleReadContainer
from zope.container.traversal import ContainerTraversable
def setUpTraversal():
    from zope.traversing.testing import setUp
    setUp()
    zope.component.provideAdapter(ContainerTraversable,
                                  (ISimpleReadContainer,), ITraversable)

#------------------------------------------------------------------------
# ISiteManager lookup
from zope.site.site import SiteManagerAdapter
from zope.component.interfaces import IComponentLookup
from zope.interface import Interface
def setUpSiteManagerLookup():
    zope.component.provideAdapter(SiteManagerAdapter, (Interface,),
                                  IComponentLookup)

#------------------------------------------------------------------------
# Placeful setup
import zope.component.hooks
from zope.app.testing.placelesssetup import setUp as placelessSetUp
from zope.app.testing.placelesssetup import tearDown as placelessTearDown
def placefulSetUp(site=False):
    placelessSetUp()
    zope.component.hooks.setHooks()
    setUpAnnotations()
    setUpDependable()
    setUpTraversal()
    setUpSiteManagerLookup()

    if site:
        site = rootFolder()
        createSiteManager(site, setsite=True)
        return site

def placefulTearDown():
    placelessTearDown()
    zope.component.hooks.resetHooks()
    zope.component.hooks.setSite()

#------------------------------------------------------------------------
# Sample Folder Creation
from zope.site.folder import Folder, rootFolder
def buildSampleFolderTree():
    # set up a reasonably complex folder structure
    #
    #     ____________ rootFolder ______________________________
    #    /                                    \                 \
    # folder1 __________________            folder2           folder3
    #   |                       \             |                 |
    # folder1_1 ____           folder1_2    folder2_1         folder3_1
    #   |           \            |            |
    # folder1_1_1 folder1_1_2  folder1_2_1  folder2_1_1

    root = rootFolder()
    root[u'folder1'] = Folder()
    root[u'folder1'][u'folder1_1'] = Folder()
    root[u'folder1'][u'folder1_1'][u'folder1_1_1'] = Folder()
    root[u'folder1'][u'folder1_1'][u'folder1_1_2'] = Folder()
    root[u'folder1'][u'folder1_2'] = Folder()
    root[u'folder1'][u'folder1_2'][u'folder1_2_1'] = Folder()
    root[u'folder2'] = Folder()
    root[u'folder2'][u'folder2_1'] = Folder()
    root[u'folder2'][u'folder2_1'][u'folder2_1_1'] = Folder()
    root[u"\N{CYRILLIC SMALL LETTER PE}"
         u"\N{CYRILLIC SMALL LETTER A}"
         u"\N{CYRILLIC SMALL LETTER PE}"
         u"\N{CYRILLIC SMALL LETTER KA}"
         u"\N{CYRILLIC SMALL LETTER A}3"] = Folder()
    root[u"\N{CYRILLIC SMALL LETTER PE}"
         u"\N{CYRILLIC SMALL LETTER A}"
         u"\N{CYRILLIC SMALL LETTER PE}"
         u"\N{CYRILLIC SMALL LETTER KA}"
         u"\N{CYRILLIC SMALL LETTER A}3"][
         u"\N{CYRILLIC SMALL LETTER PE}"
         u"\N{CYRILLIC SMALL LETTER A}"
         u"\N{CYRILLIC SMALL LETTER PE}"
         u"\N{CYRILLIC SMALL LETTER KA}"
         u"\N{CYRILLIC SMALL LETTER A}3_1"] = Folder()

    return root


#------------------------------------------------------------------------
# Sample Folder Creation
from zope.site.site import LocalSiteManager
import zope.component.interfaces

def createSiteManager(folder, setsite=False):
    if not zope.component.interfaces.ISite.providedBy(folder):
        folder.setSiteManager(LocalSiteManager(folder))
    if setsite:
        zope.component.hooks.setSite(folder)
    return zope.traversing.api.traverse(folder, "++etc++site")


#------------------------------------------------------------------------
# Local Utility Addition
def addUtility(sitemanager, name, iface, utility, suffix=''):
    """Add a utility to a site manager

    This helper function is useful for tests that need to set up utilities.
    """
    folder_name = (name or (iface.__name__ + 'Utility')) + suffix
    default = sitemanager['default']
    default[folder_name] = utility
    utility = default[folder_name]
    sitemanager.registerUtility(utility, iface, name)
    return utility


#------------------------------------------------------------------------
# Setup of test text files as modules
import sys

# Evil hack to make pickling work with classes defined in doc tests
class NoCopyDict(dict):
    def copy(self):
        return self

class FakeModule:
    """A fake module."""
    
    def __init__(self, dict):
        self.__dict = dict

    def __getattr__(self, name):
        try:
            return self.__dict[name]
        except KeyError:
            raise AttributeError(name)


def setUpTestAsModule(test, name=None):
    if name is None:
        if test.globs.has_key('__name__'):
            name = test.globs['__name__']
        else:
            name = test.globs.name

    test.globs['__name__'] = name 
    test.globs = NoCopyDict(test.globs)
    sys.modules[name] = FakeModule(test.globs)


def tearDownTestAsModule(test):
    del sys.modules[test.globs['__name__']]
    test.globs.clear()

