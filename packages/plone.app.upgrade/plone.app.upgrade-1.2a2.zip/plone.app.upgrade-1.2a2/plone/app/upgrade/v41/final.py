from Products.CMFCore.utils import getToolByName
from Products.ZCTextIndex.OkapiIndex import OkapiIndex
from BTrees.Length import Length


def fixOkapiIndexes(catalog):
    # recalculate the _totaldoclen of OkapiIndexes, because there were some
    # releases of ZCTextIndex in the wild that let it get out of whack
    for index in catalog.getIndexObjects():
        index = getattr(index, 'index', index)
        if isinstance(index, OkapiIndex):
            index._totaldoclen = Length(long(sum(index._docweight.values())))


def to411(context):
    catalog = getToolByName(context, 'portal_catalog')
    fixOkapiIndexes(catalog)
