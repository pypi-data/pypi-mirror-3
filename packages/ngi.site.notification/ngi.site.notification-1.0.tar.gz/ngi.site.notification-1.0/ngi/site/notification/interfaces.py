'''
Created on 2011/12/21

@author: nagai
'''

from zope import schema
from zope.interface import Interface

from ngi.site.notification import _


class INotificationSettings(Interface):
    """Notification settings interface
    """

    action = schema.TextLine(
                title=_(u'Action'),
                description=_(u'action_description', default=u''),
                required=True,
                default=u'publish',
                                    )
    
    comment = schema.TextLine(
                title=_(u'Comment'),
                description=_(u'comment_description', default=u''),
                required=True,
                default=_(u'was published'),
                                    )
    
    consumer_key = schema.TextLine(
                title=_(u'Consumer key'),
                description=_(u'consumer_key_description', default=u''),
                required=True,
                                    )

    consumer_secret = schema.TextLine(
                title=_(u'Consumer secret'),
                description=_(u'consumer_secret_description', default=u''),
                required=True,
                                    )
    
    access_token_key = schema.TextLine(
                title=_(u'Access token'),
                description=_(u'access_token_key_description', default=u''),
                required=True,
                                    )
        
    access_token_secret = schema.TextLine(
                title=_(u'Access token secret'),
                description=_(u'access_token_secret_description', default=u''),
                required=True,
                                    )


    