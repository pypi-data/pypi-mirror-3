#
# Copyright 2012 Corporation of Balclutha (http://www.balclutha.org)
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

import logging, transaction
from Products.ZenModel.ZenPack import ZenPack as ZenPackBase
from Products.CMFCore.DirectoryView import registerDirectory

from lbn.zenoss import packutils

from config import *
import setuphandlers

logger = logging.getLogger(PROJECTNAME)
logger.info('Installing ZenPacks.lbn.Base module')

registerDirectory(SKINS_DIR, GLOBALS)


from lbn.zenoss import packutils
import setuphandlers


class ZenPack(ZenPackBase):
    """ ZenPack for pre-loaded python modules installed in sitelib/sitearch """

    # remove loaders that attempt to do file-system stuff (ZPLDaemons,...)
    loaders = ZenPackBase.loaders[0:2] + ZenPackBase.loaders[3:]

    def install(self, pack):
        """
        Set the collector plugin
        """
        ZenPackBase.install(self, pack)

    def removeZProperties(self, app):
        """
        Remove any zProperties defined in the ZenPack

        @param app: ZenPack
        @type app: ZenPack object
        """
        for name, value, pType in self.packZProperties:
            try:
                app.zport.dmd.Devices._delProperty(name)
            except AttributeError:
                pass

def initialize(context):
    """ Zope Product """
    zport = packutils.zentinel(context)
    if zport and not packutils.hasZenPack(zport, __name__):
        logger.info('Installing into ZenPackManager')
	zpack = ZenPack(__name__)
        transaction.begin()
        zpack = packutils.addZenPack(zport, zpack)
        setuphandlers.install(zport, zpack)
        transaction.commit()
    else:
        logger.info('Already in ZenPackManager')
        
