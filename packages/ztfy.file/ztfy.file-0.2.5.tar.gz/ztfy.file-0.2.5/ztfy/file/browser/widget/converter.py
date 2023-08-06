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
from cStringIO import StringIO
from PIL import Image

# import Zope3 interfaces
from z3c.form.interfaces import IWidget, NOT_CHANGED

# import local interfaces
from ztfy.file.interfaces import IFileField, IImageField, ICthumbImageField, ICthumbImageFieldData

# import Zope3 packages
from z3c.form.converter import FileUploadDataConverter, FormatterValidationError
from zope.component import adapts
from zope.interface import implements

# import local packages
from ztfy.file.display import ThumbnailGeometry

from ztfy.file import _


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


class ImageFieldDataConverter(FileFieldDataConverter):
    """Data converter for ImageField fields"""

    adapts(IImageField, IWidget)

    def toFieldValue(self, value):
        result = super(ImageFieldDataConverter, self).toFieldValue(value)
        if (result is not None) and (result is not NOT_CHANGED):
            try:
                Image.open(StringIO(result))
            except:
                raise FormatterValidationError(_("Given file is not in a recognized image format"), value)
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
