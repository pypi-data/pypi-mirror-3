from zope import component, interface
from zope.interface import implements
try:
    from zope.component.interfaces import ObjectEvent
except:
    from zope.app.event.objectevent import ObjectEvent

from zope.event import notify
from Products.CMFCore.utils import getToolByName
import interfaces

from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

import email.MIMEText
from email.Header import Header
from email.Message import Message
from email import message_from_string
from zope.sendmail.interfaces import IMailDelivery
from zope.component import getUtility

class EnvironmentCreationEvent( ObjectEvent ):

    implements( interfaces.IEnvironmentCreationEvent )
    
    def __init__( self, object, item, environment_interface ):
        super( EnvironmentCreationEvent, self).__init__( object )
        self.item = item
        self.environment_interface = environment_interface

def environment_created(object, event):
    object.reindexObject()

class EnvironmentModificationEvent( ObjectEvent ):

    implements( interfaces.IEnvironmentModificationEvent )
    
    def __init__( self, object, item, environment_interface ):
        super( EnvironmentModificationEvent, self).__init__( object )
        self.item = item
        self.environment_interface = environment_interface

def environment_modified(object, event):
    object.reindexObject()
