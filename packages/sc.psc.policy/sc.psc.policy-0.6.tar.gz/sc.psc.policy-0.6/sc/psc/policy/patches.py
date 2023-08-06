# -*- coding:utf-8 -*-
from collective.psc.blobstorage import BlobWrapper


def __init__(self, content_type='PSCFile'):
    ''' Set a default content_type for BlobWrapper '''
    super(BlobWrapper, self).__init__(content_type)


def run():
    # Patch BlobField
    setattr(BlobWrapper, '__init__', __init__)
