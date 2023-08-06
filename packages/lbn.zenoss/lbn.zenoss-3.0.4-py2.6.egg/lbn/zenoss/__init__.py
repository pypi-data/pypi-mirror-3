#
#    Copyright 2010-2012 Corporation of Balclutha (http://www.balclutha.org)
# 
#                All Rights Reserved
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
from App.ImageFile import ImageFile
from Products.ZenModel.ZenPack import ZenPack as ZenPackBase
from packutils import zentinel


class ZenPack(ZenPackBase):
    """ Zenoss eggy thing - placeholder to shim if ever required """

def initialize(context):
    """
    function to hack zope instance upon startup
    """
    zport = zentinel(context)

GLOBALS = globals()
misc_ = {}
for icon in ('ZenossInfo_icon', 'RelationshipManager_icon', 'portletmanager'):
    misc_[icon] = ImageFile('www/%s.gif' % icon, GLOBALS)


#
# unilaterally apply monkeypatches to running Zope server
#
import monkeypatches
