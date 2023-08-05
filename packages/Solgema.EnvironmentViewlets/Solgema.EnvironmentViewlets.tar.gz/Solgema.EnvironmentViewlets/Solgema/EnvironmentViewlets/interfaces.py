import datetime
from zope.interface import Interface, Attribute, directlyProvides
from zope import schema
from zope.schema.interfaces import ValidationError
from zope.app.component.hooks import getSite
from zope.contentprovider.interfaces import ITALNamespaceData
from zope.app.form.interfaces import IInputWidget, IDisplayWidget
from zope.app.container.interfaces import IContainer
from zope.app.container.interfaces import IContainerNamesContainer
from zope.app.container.interfaces import IAdding
from zope.publisher.interfaces.browser import IBrowserRequest
from plone.theme.interfaces import IDefaultPloneLayer
from zope.viewlet.interfaces import IViewletManager
import zope.viewlet.interfaces
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from Products.ATContentTypes.interface import IATFolder
from Products.CMFCore.utils import getToolByName
from zope.viewlet.interfaces import IViewletManager

from zope.app.publisher.interfaces.browser import IBrowserMenu
from zope.app.publisher.interfaces.browser import IBrowserSubMenuItem

from zope.contentprovider.interfaces import IContentProvider
from zope.app.form.browser import interfaces as izafb
try:
    from zope.component.interfaces import IObjectEvent
except ImportError:
    # BBB for Zope 2.9
    from zope.app.event.interfaces import IObjectEvent

from zope.schema import interfaces as izs
from zope.interface import Interface

from zope.app.container.constraints import contains

from Solgema.EnvironmentViewlets.config import _sbd

###### INTERFACES

class IPersistentOptions( Interface ):
    """
    a base interface that our persistent option annotation settings,
    can adapt to. specific schemas that want to have context stored
    annotation values should subclass from this interface, so they
    use adapation to get access to persistent settings. for example,
    settings = IMySettings(context)
    """

class ISolgemaEnvironmentViewletsLayer( IDefaultPloneLayer ):
    """Solgema Immo layer""" 

class IBandeauMarker( Interface ):
    """Marker for Real Estate Content"""

class IBandeauContent( Interface ):
    """
    Bandeau informations
    """

    bannerLocalOnly = schema.Bool(
        title = _sbd(u"label_bannerLocalOnly", default=(u"Local Banner")),
        description=_sbd(u'help_bannerLocalOnly', default=u"Display the banner in the current folder only"),
        required = False,
        default = False,
        )

    bannerStopAcquisition = schema.Bool(
        title = _sbd(u"label_bannerStopAcquisition", default=(u"Stop Acquisition")),
        description=_sbd(u'help_bannerStopAcquisition', default=u"Stop banners research to this folder and don't display banners in upper folders"),
        required = False,
        default = True,
        )

class IFooterMarker( Interface ):
    """Marker for Real Estate Content"""

class IFooterContent( Interface ):
    """
    Bandeau informations
    """

    footerLocalOnly = schema.Bool(
        title = _sbd(u"label_footerLocalOnly", default=(u"Local Footer")),
        description=_sbd(u'help_footerLocalOnly', default=u"Display the footer in the current folder only"),
        required = False,
        default = False,
        )

    footerStopAcquisition = schema.Bool(
        title = _sbd(u"label_footerStopAcquisition", default=(u"Stop Acquisition")),
        description=_sbd(u'help_footerStopAcquisition', default=u"Stop footers research to this folder and don't display footers in upper folders"),
        required = False,
        default = True,
        )

class IPrintFooterMarker( Interface ):
    """Marker for Real Estate Content"""

class IPrintFooterContent( Interface ):
    """
    Bandeau informations
    """

    printfooterLocalOnly = schema.Bool(
        title = _sbd(u"label_printfooterLocalOnly", default=(u"Local Footer")),
        description=_sbd(u'help_printfooterLocalOnly', default=u"Display the footer in the current folder only"),
        required = False,
        default = False,
        )

    printfooterStopAcquisition = schema.Bool(
        title = _sbd(u"label_printfooterStopAcquisition", default=(u"Stop Acquisition")),
        description=_sbd(u'help_printfooterStopAcquisition', default=u"Stop footers research to this folder and don't display footers in upper folders"),
        required = False,
        default = True,
        )

class ILogoMarker( Interface ):
    """Marker for Real Estate Content"""

class ILogoContent( Interface ):
    """
    Bandeau informations
    """

    logoLocalOnly = schema.Bool(
        title = _sbd(u"label_logoLocalOnly", default=(u"Local Logo")),
        description=_sbd(u'help_logoLocalOnly', default=u"Display the logo in the current folder only"),
        required = False,
        default = False,
        )

class IPrintLogoMarker( Interface ):
    """Marker for Real Estate Content"""

class IPrintLogoContent( Interface ):
    """
    Bandeau informations
    """

    printlogoLocalOnly = schema.Bool(
        title = _sbd(u"label_printlogoLocalOnly", default=(u"Local Print Logo")),
        description=_sbd(u'help_printlogoLocalOnly', default=u"Display the logo for pinting in the current folder only"),
        required = False,
        default = False,
        )

class IEnvironmentCreationEvent( IObjectEvent ):
    """ sent out when a payable is created
    """

    item = Attribute("object implementing environment interface")    
    environment_interface = Attribute("environment interface the object implements")

class IEnvironmentModificationEvent( IEnvironmentCreationEvent ):
    """"""


######################################3

class ISolgemaBandeauManager(IViewletManager):
    """bandeauManager"""

class ISolgemaFooterManager(IViewletManager):
    """bandeauManager"""

class ISolgemaPrintFooterManager(IViewletManager):
    """bandeauManager"""

################# MENU

class ISolgemaEnvironmentActionsSubMenuItem(IBrowserSubMenuItem):
    """The menu item linking to the actions menu.
    """

class ISolgemaEnvironmentActionsMenu(IBrowserMenu):
    """The actions menu.

    This gets its menu items from portal_actions.
    """
