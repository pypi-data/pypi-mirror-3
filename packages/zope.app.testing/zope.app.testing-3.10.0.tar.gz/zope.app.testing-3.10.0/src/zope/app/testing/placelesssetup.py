##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
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
"""Unit test logic for setting up and tearing down basic infrastructure

$Id: placelesssetup.py 110724 2010-04-11 00:04:11Z tseaver $
"""
from zope.schema.vocabulary import setVocabularyRegistry
from zope.component.testing import PlacelessSetup as CAPlacelessSetup
from zope.component.eventtesting import PlacelessSetup as EventPlacelessSetup
from zope.i18n.testing import PlacelessSetup as I18nPlacelessSetup
from zope.password.testing import setUpPasswordManagers
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.traversing.browser.absoluteurl import AbsoluteURL

from zope.app.testing import ztapi
from zope.container.testing import PlacelessSetup as ContainerPlacelessSetup

class PlacelessSetup(CAPlacelessSetup,
                     EventPlacelessSetup,
                     I18nPlacelessSetup,
                     ContainerPlacelessSetup):

    def setUp(self, doctesttest=None):
        CAPlacelessSetup.setUp(self)
        EventPlacelessSetup.setUp(self)
        ContainerPlacelessSetup.setUp(self)
        I18nPlacelessSetup.setUp(self)

        setUpPasswordManagers()
        ztapi.browserView(None, 'absolute_url', AbsoluteURL)
        ztapi.browserViewProviding(None, AbsoluteURL, IAbsoluteURL)

        from zope.security.testing import addCheckerPublic
        addCheckerPublic()

        from zope.security.management import newInteraction
        newInteraction()

        setVocabularyRegistry(None)


ps = PlacelessSetup()
setUp = ps.setUp

def tearDown():
    tearDown_ = ps.tearDown
    def tearDown(doctesttest=None):
        tearDown_()
    return tearDown

tearDown = tearDown()

del ps
