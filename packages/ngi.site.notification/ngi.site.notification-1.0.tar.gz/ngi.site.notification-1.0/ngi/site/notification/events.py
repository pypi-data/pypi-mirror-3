# encoding: utf-8
'''
Created on 2011/12/21

@author: nagai
'''

from five import grok
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from Products.ATContentTypes.interfaces.interfaces import IATContentType
from Products.CMFCore.interfaces import IActionSucceededEvent
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
import twitter
import datetime
    

@grok.subscribe(IATContentType, IActionSucceededEvent)
def statechangedNotification(ob, action):
    registry = getUtility(IRegistry)
    action_name = registry['ngi.site.notification.interfaces.INotificationSettings.action']
    consumer_key = registry['ngi.site.notification.interfaces.INotificationSettings.consumer_key']
    consumer_secret = registry['ngi.site.notification.interfaces.INotificationSettings.consumer_secret']
    access_token_key = registry['ngi.site.notification.interfaces.INotificationSettings.access_token_key']
    access_token_secret = registry['ngi.site.notification.interfaces.INotificationSettings.access_token_secret']
    comment = registry['ngi.site.notification.interfaces.INotificationSettings.comment']
    if action_name and consumer_key and consumer_secret and access_token_key and access_token_secret:
        if action_name == action.action:
            api = twitter.Api(
                              consumer_key = consumer_key,
                              consumer_secret = consumer_secret,
                              access_token_key = access_token_key,
                              access_token_secret = access_token_secret)
            now = datetime.datetime.now()
            status = u'%s %s %s %s' % (now.strftime('%m/%d'), ob.Title().decode('utf-8'), comment, ob.absolute_url())
            api.PostUpdate(status.encode('utf-8'))

