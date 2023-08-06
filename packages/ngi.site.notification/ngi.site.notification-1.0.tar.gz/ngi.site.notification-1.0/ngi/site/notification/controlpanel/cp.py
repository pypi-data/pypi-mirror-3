# -*- coding: utf-8 -*-
'''
cp.py

Created on 2011/12/21

@author: nagai
'''

from plone.app.registry.browser import controlpanel
from ngi.site.notification.interfaces import INotificationSettings
from ngi.site.notification import _


class NotificationSettingsEditForm(controlpanel.RegistryEditForm):
    
    schema = INotificationSettings
    label = _(u"Notification settings") 
    

class NotificationSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = NotificationSettingsEditForm

