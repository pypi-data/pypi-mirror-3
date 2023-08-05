# Make sure that catalog brains can have a 'price' attribute.
from zope import component
from zope.app.component.hooks import getSite
from Products.CMFPlone import CatalogTool
from Products.CMFCore.utils import getToolByName
from plone.indexer.decorator import indexer

from Solgema.EnvironmentViewlets.interfaces import IBandeauMarker, IBandeauContent, IFooterMarker, IFooterContent, IPrintFooterMarker, IPrintFooterContent, ILogoMarker, ILogoContent, IPrintLogoMarker, IPrintLogoContent

@indexer(IBandeauMarker)
def get_local_banner(object):
    if not IBandeauMarker.providedBy(object):
        return None
    adapted = IBandeauContent(object, None)
    if adapted is not None:
        return adapted.bannerLocalOnly
    return None

@indexer(IBandeauMarker)
def get_stopacquisition_banner(object):
    if not IBandeauMarker.providedBy(object):
        return None
    adapted = IBandeauContent(object, None)
    if adapted is not None:
        return adapted.bannerStopAcquisition
    return None

@indexer(IFooterMarker)
def get_local_footer(object):
    if not IFooterMarker.providedBy(object):
        return None
    adapted = IFooterContent(object, None)
    if adapted is not None:
        return adapted.footerLocalOnly
    return None

@indexer(IFooterMarker)
def get_stopacquisition_footer(object):
    if not IFooterMarker.providedBy(object):
        return None
    adapted = IFooterContent(object, None)
    if adapted is not None:
        return adapted.footerStopAcquisition
    return None

@indexer(IPrintFooterMarker)
def get_local_printfooter(object):
    if not IPrintFooterMarker.providedBy(object):
        return None
    adapted = IPrintFooterContent(object, None)
    if adapted is not None:
        return adapted.printfooterLocalOnly
    return None

@indexer(IPrintFooterMarker)
def get_stopacquisition_printfooter(object):
    if not IPrintFooterMarker.providedBy(object):
        return None
    adapted = IPrintFooterContent(object, None)
    if adapted is not None:
        return adapted.printfooterStopAcquisition
    return None

@indexer(ILogoMarker)
def get_local_logo(object):
    if not ILogoMarker.providedBy(object):
        return None
    adapted = ILogoContent(object, None)
    if adapted is not None:
        return adapted.logoLocalOnly
    return None

@indexer(IPrintLogoMarker)
def get_local_printlogo(object):
    if not IPrintLogoMarker.providedBy(object):
        return None
    adapted = IPrintLogoContent(object, None)
    if adapted is not None:
        return adapted.printlogoLocalOnly
    return None

