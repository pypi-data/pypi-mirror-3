from Acquisition import aq_inner, aq_parent, aq_base
from zope.interface import implements, alsoProvides
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.viewlet.interfaces import IViewlet
from zope.deprecation.deprecation import deprecate
from Products.CMFPlone import utils
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.ATContentTypes.interface import IATFolder
import sys, os
from zope.app.publisher.interfaces.browser import IBrowserMenu
import Globals
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.root import getNavigationRoot
from plone.app.layout.navigation.navtree import buildFolderTree

from plone.app.layout.viewlets.common import ViewletBase
from plone.app.layout.viewlets.common import PathBarViewlet as newPathBarViewlet
from plone.app.layout.viewlets.common import PersonalBarViewlet as newPersonalBarViewlet
from plone.app.layout.viewlets.content import DocumentActionsViewlet as newDocumentActionsViewlet
from plone.app.layout.viewlets.content import WorkflowHistoryViewlet as newWorkflowHistoryViewlet
from plone.app.layout.icons.icons import PloneSiteContentIcon as newPloneSiteContentIcon
from plone.app.contentmenu.view import ContentMenuProvider as newContentMenuProvider

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile, BoundPageTemplate
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from plone.memoize import instance, view, ram
from time import time

from Products.Five import BrowserView

def findTraverseObject(context, filter={}, nbr=1, full_objects=False):

    portal = getToolByName(context, 'portal_url').getPortalObject()
    result = []

    cresults = portal.portal_catalog.searchResults(**filter)
    results = [a for a in cresults if '/'.join(a.getPath().split('/')[:-1]) in '/'.join(context.getPhysicalPath())]
    results.sort(lambda x, y : cmp (len(x.getPath().split('/')), len(y.getPath().split('/'))))
    results.reverse()
    if full_objects:
        return [a.getObject() for a in results[0:nbr]]
    return results[0:nbr]

class ObjectView(BrowserView):

    def __init__( self, context, request, templatename ):
        self.context = context
        self.request = request
        pt = ViewPageTemplateFile(templatename)
        self.template = BoundPageTemplate(pt, self)

    def __call__(self):
        return self.template()

class BandeauManagerViewlet(ViewletBase):
    index = ViewPageTemplateFile('bandeauManager.pt')

class BandeauViewlet(ViewletBase):
    index = ViewPageTemplateFile('bandeau.pt')
    marker = 'Solgema.EnvironmentViewlets.interfaces.IBandeauMarker'

    @view.memoize
    def getSolgemaBandeaux(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        context = self.context

        while not IATFolder.providedBy(context) and not IPloneSiteRoot.providedBy(context):
            context = aq_parent(aq_inner(context))

        finalList = context.getFolderContents(contentFilter={'object_provides':self.marker,
                                                             'review_state':['published','visible'],
                                                             'sort_on':'getObjPositionInParent'})

        itemsStop = context.getFolderContents(contentFilter={'stopAcquisitionBanner':{'query':True},
                                                             'review_state':['published','visible']})

        if not itemsStop and not IPloneSiteRoot.providedBy(context):
            parent = context
            while not itemsStop:
                parent = aq_parent(aq_inner(parent))
                if IPloneSiteRoot.providedBy(parent):
                    finalList += parent.getFolderContents(contentFilter={'object_provides':self.marker,
                                                                         'review_state':['published','visible'],
                                                                         'sort_on':'getObjPositionInParent',
                                                                         'localBanner':{'query':False}} )
                    break

                itemsStop = parent.getFolderContents(contentFilter={'stopAcquisitionBanner':{'query':True},
                                                                    'review_state':['published','visible']})

                finalList += parent.getFolderContents(contentFilter={'object_provides':self.marker,
                                                                     'review_state':['published','visible'],
                                                                     'sort_on':'getObjPositionInParent',
                                                                     'localBanner':{'query':False}} )
        bandeaux = [a.getObject() for a in finalList]

        bandeauxList = []
        for bandeau in bandeaux:
            if hasattr(bandeau, 'tag'):
                height = bandeau.getHeight()
                url = bandeau.absolute_url()
                title = bandeau.Description()
                backgrounddiv = '<div style="height:%spx; width:100%%; background:transparent url(%s) no-repeat scroll left top;" title="%s" class="bandeau_image"></div>' % (height, url, title)
#                bandeauxList.append({'id':bandeau.id, 'content':bandeau.tag(title=bandeau.Description())})
                bandeauxList.append({'id':bandeau.id, 'content':backgrounddiv})
            if hasattr(bandeau, 'getText'):
                bandeauxList.append({'id':bandeau.id, 'content':bandeau.getText()})
            if bandeau.portal_type == 'Collage':
                bandeauxList.append({'id':bandeau.id, 'content':ObjectView(bandeau, self.request,'collage_renderer.pt' )})
            if bandeau.portal_type == 'FlashMovie':
                bandeauxList.append({'id':bandeau.id, 'content':ObjectView(bandeau, self.request,'flashmovie_macro_flashobject.pt' )})
        return bandeauxList

    def update(self):
        super(BandeauViewlet, self).update()
        self.bandeauxList = self.getSolgemaBandeaux()
        self.portal_title = self.portal_state.portal_title()

class FooterManagerViewlet(ViewletBase):
    index = ViewPageTemplateFile('footerManager.pt')

class FooterViewlet(BandeauViewlet):
    index = ViewPageTemplateFile('footer.pt')
    marker = 'Solgema.EnvironmentViewlets.interfaces.IFooterMarker'

    @view.memoize
    def getSolgemaFooter(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        context = self.context

        while not IATFolder.providedBy(context) and not IPloneSiteRoot.providedBy(context):
            context = aq_parent(aq_inner(context))

        finalList = context.getFolderContents(contentFilter={'object_provides':self.marker,
                                                             'review_state':['published','visible'],
                                                             'sort_on':'getObjPositionInParent'})

        itemsStop = context.getFolderContents(contentFilter={'stopAcquisitionFooter':{'query':True},
                                                             'review_state':['published','visible']})

        if not itemsStop and not IPloneSiteRoot.providedBy(context):
            parent = context
            while not itemsStop:
                parent = aq_parent(aq_inner(parent))
                if IPloneSiteRoot.providedBy(parent):
                    finalList += parent.getFolderContents(contentFilter={'object_provides':self.marker,
                                                                         'review_state':['published','visible'],
                                                                         'sort_on':'getObjPositionInParent',
                                                                         'localFooter':{'query':False}})
                    break

                itemsStop = parent.getFolderContents(contentFilter={'stopAcquisitionFooter':{'query':True},
                                                                    'review_state':['published','visible']})

                finalList += parent.getFolderContents(contentFilter={'object_provides':self.marker,
                                                                     'review_state':['published','visible'],
                                                                     'sort_on':'getObjPositionInParent',
                                                                     'localFooter':{'query':False}} )
        bandeaux = [a.getObject() for a in finalList]

        bandeauxList = []
        for bandeau in bandeaux:
            if hasattr(bandeau, 'tag'):
                height = bandeau.getHeight()
                url = bandeau.absolute_url()
                title = bandeau.Description()
                backgrounddiv = '<div style="height:%spx; width:100%%; background:transparent url(%s) no-repeat scroll left top;" title="%s" class="bandeau_image"></div>' % (height, url, title)
#                bandeauxList.append({'id':bandeau.id, 'content':bandeau.tag(title=bandeau.Description())})
                bandeauxList.append({'id':bandeau.id, 'content':backgrounddiv})
            if hasattr(bandeau, 'getText'):
                bandeauxList.append({'id':bandeau.id, 'content':bandeau.getText()})
            if bandeau.portal_type == 'Collage':
                bandeauxList.append({'id':bandeau.id, 'content':ObjectView(bandeau, self.request,'collage_renderer.pt' )})
            if bandeau.portal_type == 'FlashMovie':
                bandeauxList.append({'id':bandeau.id, 'content':ObjectView(bandeau, self.request,'flashmovie_macro_flashobject.pt' )})
        return bandeauxList

    def update(self):
        super(BandeauViewlet, self).update()
        self.bandeauxList = self.getSolgemaFooter()
        self.portal_title = self.portal_state.portal_title()

class PrintFooterManagerViewlet(ViewletBase):
    index = ViewPageTemplateFile('printfooterManager.pt')

class PrintFooterViewlet(BandeauViewlet):
    index = ViewPageTemplateFile('printfooter.pt')
    marker = 'Solgema.EnvironmentViewlets.interfaces.IPrintFooterMarker'

    @view.memoize
    def getSolgemaPrintFooter(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        context = self.context

        while not IATFolder.providedBy(context) and not IPloneSiteRoot.providedBy(context):
            context = aq_parent(aq_inner(context))

        finalList = context.getFolderContents(contentFilter={'object_provides':self.marker,
                                                             'review_state':['published','visible'],
                                                             'sort_on':'getObjPositionInParent'})

        itemsStop = context.getFolderContents(contentFilter={'stopAcquisitionPrintFooter':{'query':True},
                                                             'review_state':['published','visible']})

        if not itemsStop and not IPloneSiteRoot.providedBy(context):
            parent = context
            while not itemsStop:
                parent = aq_parent(aq_inner(parent))
                if IPloneSiteRoot.providedBy(parent):
                    finalList += parent.getFolderContents(contentFilter={'object_provides':self.marker,
                                                                         'review_state':['published','visible'],
                                                                         'sort_on':'getObjPositionInParent',
                                                                         'localprintFooter':{'query':False}})
                    break

                itemsStop = parent.getFolderContents(contentFilter={'stopAcquisitionPrintFooter':{'query':True},
                                                                    'review_state':['published','visible']})

                finalList += parent.getFolderContents(contentFilter={'object_provides':self.marker,
                                                                     'review_state':['published','visible'],
                                                                     'sort_on':'getObjPositionInParent',
                                                                     'localPrintFooter':{'query':False}} )
        bandeaux = [a.getObject() for a in finalList]

        bandeauxList = []
        for bandeau in bandeaux:
            if hasattr(bandeau, 'tag'):
                height = bandeau.getHeight()
                url = bandeau.absolute_url()
                title = bandeau.Description()
                backgrounddiv = '<div style="height:%spx; width:100%%; background:transparent url(%s) no-repeat scroll left top;" title="%s" class="bandeau_image"></div>' % (height, url, title)
#                bandeauxList.append({'id':bandeau.id, 'content':bandeau.tag(title=bandeau.Description())})
                bandeauxList.append({'id':bandeau.id, 'content':backgrounddiv})
            if hasattr(bandeau, 'getText'):
                bandeauxList.append({'id':bandeau.id, 'content':bandeau.getText()})
            if bandeau.portal_type == 'Collage':
                bandeauxList.append({'id':bandeau.id, 'content':ObjectView(bandeau, self.request,'collage_renderer.pt' )})
            if bandeau.portal_type == 'FlashMovie':
                bandeauxList.append({'id':bandeau.id, 'content':ObjectView(bandeau, self.request,'flashmovie_macro_flashobject.pt' )})
        return bandeauxList

    def update(self):
        super(BandeauViewlet, self).update()
        self.bandeauxList = self.getSolgemaPrintFooter()
        self.portal_title = self.portal_state.portal_title()

class LogoViewlet(BandeauViewlet):
    index = ViewPageTemplateFile('logo.pt')
    marker = 'Solgema.EnvironmentViewlets.interfaces.ILogoMarker'

    @view.memoize
    def getSolgemaLogo(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        context = self.context

        while not IATFolder.providedBy(context) and not IPloneSiteRoot.providedBy(context):
            context = aq_parent(aq_inner(context))

        finalList = context.getFolderContents(contentFilter={'object_provides':self.marker,
                                                             'review_state':['published','visible'],
                                                             'sort_on':'getObjPositionInParent'})

        if not finalList and not IPloneSiteRoot.providedBy(context):
            parent = context
            while not finalList:
                parent = aq_parent(aq_inner(parent))
                if IPloneSiteRoot.providedBy(parent):
                    finalList += parent.getFolderContents(contentFilter={'object_provides':self.marker,
                                                                         'review_state':['published','visible'],
                                                                         'sort_on':'getObjPositionInParent',
                                                                         'localLogo':{'query':False}})
                    break

                finalList += parent.getFolderContents(contentFilter={'object_provides':self.marker,
                                                                     'review_state':['published','visible'],
                                                                     'sort_on':'getObjPositionInParent',
                                                                     'localLogo':{'query':False}} )

        bandeaux = finalList and [finalList[0].getObject(),] or []

        bandeauxList = []
        for bandeau in bandeaux:
            if hasattr(bandeau, 'tag'):
                bandeauxList.append({'id':bandeau.id, 'content':bandeau.tag(title=bandeau.Description())})
            if hasattr(bandeau, 'getText'):
                bandeauxList.append({'id':bandeau.id, 'content':bandeau.getText()})
            if bandeau.portal_type == 'FlashMovie':
                bandeauxList.append({'id':bandeau.id, 'content':ObjectView(bandeau, self.request,'flashmovie_macro_flashobject.pt' )})
        return bandeauxList and bandeauxList[0] or None

    def update(self):
        super(BandeauViewlet, self).update()
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        self.portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        self.wholeLogoHTML = self.getSolgemaLogo() and '<a id="portal-logo" href="%s" accesskey="1" class="visualNoPrint">%s</a>' % (portal.absolute_url(), self.getSolgemaLogo()['content']) or ''
        self.portal_title = self.portal_state.portal_title()



class PrintLogoViewlet(BandeauViewlet):
    index = ViewPageTemplateFile('printlogo.pt')
    marker = 'Solgema.EnvironmentViewlets.interfaces.IPrintLogoMarker'

    @view.memoize
    def getSolgemaPrintLogo(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        context = self.context

        while not IATFolder.providedBy(context) and not IPloneSiteRoot.providedBy(context):
            context = aq_parent(aq_inner(context))

        finalList = context.getFolderContents(contentFilter={'object_provides':self.marker,
                                                             'review_state':['published','visible'],
                                                             'sort_on':'getObjPositionInParent'})

        if not finalList and not IPloneSiteRoot.providedBy(context):
            parent = context
            while not finalList:
                parent = aq_parent(aq_inner(parent))
                if IPloneSiteRoot.providedBy(parent):
                    finalList += parent.getFolderContents(contentFilter={'object_provides':self.marker,
                                                                         'review_state':['published','visible'],
                                                                         'sort_on':'getObjPositionInParent',
                                                                         'localPrintLogo':{'query':False}})
                    break

                finalList += parent.getFolderContents(contentFilter={'object_provides':self.marker,
                                                                     'review_state':['published','visible'],
                                                                     'sort_on':'getObjPositionInParent',
                                                                     'localPrintLogo':{'query':False}} )

        bandeaux = finalList and [finalList[0].getObject(),] or []

        bandeauxList = []
        for bandeau in bandeaux:
            if hasattr(bandeau, 'tag'):
                bandeauxList.append({'id':bandeau.id, 'content':bandeau.tag(title=bandeau.Description())})
            if hasattr(bandeau, 'getText'):
                bandeauxList.append({'id':bandeau.id, 'content':bandeau.getText()})
            if bandeau.portal_type == 'Collage':
                bandeauxList.append({'id':bandeau.id, 'content':ObjectView(bandeau, self.request,'collage_renderer.pt' )})
            if bandeau.portal_type == 'FlashMovie':
                bandeauxList.append({'id':bandeau.id, 'content':ObjectView(bandeau, self.request,'flashmovie_macro_flashobject.pt' )})
        return bandeauxList and bandeauxList[0] or None

    def update(self):
        super(BandeauViewlet, self).update()
        self.portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        self.navigation_root_url = self.portal_state.navigation_root_url()
        self.bandeauxList = self.getSolgemaPrintLogo()
        self.portal_title = self.portal_state.portal_title()

