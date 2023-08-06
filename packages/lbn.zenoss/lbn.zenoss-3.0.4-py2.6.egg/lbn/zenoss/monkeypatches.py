#
# Copyright 2010-2012 Corporation of Balclutha (http://www.balclutha.org)
# 
#                All Rights Reserved
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
#
# Corporation of Balclutha DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS, IN NO EVENT SHALL Corporation of Balclutha BE LIABLE FOR
# ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE. 
#
import logging, os, OFS
from App.special_dtml import DTMLFile

logger = logging.getLogger('lbn.zenoss')


def noop(*args, **kw): pass

#
# seems that this pesky function is removing inituser without successfully
# installing it ...
#
logger.info('monkeypatching ZenUtils.Security')
from Products.ZenUtils import Security
Security._createInitialUser = noop


#
# add password type into Properties on ZMI (but since these aren't writable, it's moot)
#
from ZPublisher.Converters import type_converters, field2string
type_converters['password'] = field2string

from Products.ZenModel.ZenModelRM import ZenModelRM
ZenModelRM.manage_propertiesForm = DTMLFile('dtml/properties', globals(), property_extensible_schema__=1)

logger.info('added type converter: password')


from Products.ZenRelations.ToManyRelationshipBase import ToManyRelationshipBase, RelationshipBase
ToManyRelationshipBase.manage_options = ToManyRelationshipBase.manage_options + OFS.SimpleItem.SimpleItem.manage_options

from Products.ZenRelations.ToManyRelationship import ToManyRelationship
_remoteRemoveOrig = ToManyRelationship._remoteRemove

def _remoteRemove(self, obj=None):
    """
    remove an object from the far side of this relationship
    if no object is passed in remove all objects
    """
    # seems the original barfs on trying to delete non-existing relations ...
    try:
        _remoteRemoveOrig(self, obj)
    except (AttributeError, ValueError):
        pass

ToManyRelationship._remoteRemove = _remoteRemove

from Products.ZenWidgets.PortletManager import PortletManager
PortletManager.icon = 'misc_/lbn.zenoss/portletmanager'

from Products.ZenModel.ZenossInfo import ZenossInfo
ZenossInfo.icon = 'misc_/lbn.zenoss/ZenossInfo_icon'

from Products.ZenRelations.RelationshipManager import RelationshipManager
RelationshipManager.icon = 'misc_/lbn.zenoss/RelationshipManager_icon'

logger.info('added ZMI icons')

# TODO - override RelationshipManager.manage_workspace to be default ...

# note that we're also strapping an implements(IItem) via zcml ...
import AccessControl
from Products.ZenRelations.ZItem import ZItem

ZItem.manage_options = AccessControl.Owned.Owned.manage_options + ( 
    {'label':'Interfaces', 'action':'manage_interfaces'}, 
    ) 


#
# the Skin registration stuff is borked for python modules, but we want to retain
# them for other zenpacks where it might still work ...
#
from Products.ZenUtils import Skins

findZenPackRootOrig = Skins.findZenPackRoot
def findZenPackRoot(base):
    # pure python module search
    if base.find('site-packages') != -1:
        dirs = base.split(os.path.sep)
        ndx = dirs.index('site-packages')
        return '.'.join(dirs[ndx + 1:-1])

    # Zenoss ZenPacks stored in Zenoss Tree
    return findZenPackRootOrig(base)

Skins.findZenPackRoot = findZenPackRoot


from Products.ZenModel.ZenPackLoader import ZPLSkins
ZPLSkinsload = ZPLSkins.load
ZPLSkinsunload = ZPLSkins.unload

def skinLoad(self, pack, app):
    try:
	ZPLSkinsload(self, pack, app)
    except Exception, e:
	logger.warn(str(e), exc_info=True)

def skinUnload(self, pack, app, leaveObjects=False):
    try:
	ZPLSkinsunload(self, pack, app, leaveObjects)
    except Exception, e:
	logger.warn(str(e), exc_info=True)

ZPLSkins.load = skinLoad
ZPLSkins.unload = skinUnload


from Products.ZenUtils.CmdBase import CmdBase
getConfigFileDefaultsOrig = CmdBase.getConfigFileDefaults
def getConfigFileDefaults(self, filename):
    """
    Parse a config file 
    """
    try:
        getConfigFileDefaultsOrig(self, filename)
    except IOError:
        pass

CmdBase.getConfigFileDefaults = getConfigFileDefaults
    
logger.info('stop zope.conf being stomped on')
