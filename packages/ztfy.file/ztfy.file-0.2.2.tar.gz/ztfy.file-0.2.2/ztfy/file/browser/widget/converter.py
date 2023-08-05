### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008 Thierry Florac <tflorac AT ulthar.net>
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


# import standard packages

# import Zope3 interfaces
from z3c.form.interfaces import IWidget, NOT_CHANGED

# import local interfaces
from ztfy.file.interfaces import IFileField, ICthumbImageField, ICthumbImageFieldData

# import Zope3 packages
from z3c.form.converter import FileUploadDataConverter
from zope.component import adapts
from zope.interface import implements

# import local packages
from ztfy.file.display import ThumbnailGeometry


class FileFieldDataConverter(FileUploadDataConverter):
    """Data converter for FileField fields"""

    adapts(IFileField, IWidget)

    def toFieldValue(self, value):
        result = super(FileFieldDataConverter, self).toFieldValue(value)
        if result is NOT_CHANGED:
            widget = self.widget
            if widget.deleted:
                return None
        return result


class CthumbImageFieldData(object):

    implements(ICthumbImageFieldData)

    def __init__(self, value, geometry):
        self.value = value
        self.geometry = geometry


class CthumbImageFieldDataConverter(FileFieldDataConverter):
    """Data converter for CthumbImageField fields"""

    adapts(ICthumbImageField, IWidget)

    def toFieldValue(self, value):
        result = super(CthumbImageFieldDataConverter, self).toFieldValue(value)
        widget = self.widget
        return CthumbImageFieldData(result, ThumbnailGeometry(widget.position, widget.size))
