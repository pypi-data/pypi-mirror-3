# -*- coding: utf-8 -*-
#
# File: SimpleCalendar.py
#
# Copyright (c) 2008 by 
# Generator: ArchGenXML Version 2.0
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """unknown <unknown>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements
from dateable.chronos.interfaces import ICalendarEnhanced, IPossibleCalendar, IEvent
from dateable.kalends import IEventProvider

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
from Products.SimpleCalendar import SimpleCalendarMessageFactory as _

from Products.SimpleCalendar.config import *
from Products.CMFCore.utils import getToolByName

from DateTime import DateTime

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((
#    LinesField('item_states',
#         widget=LinesWidget(label = _(u'item_states', default=u'Event states we will show')),),
),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

SimpleCalendar_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

def filter_exclude_paths(objects, paths):
    """Removes objects with paths."""
    objects_ = []
    for object in objects:
        for path in paths:
            if '/'.join(object.getPhysicalPath()).startswith(path):
                break
        else:
            objects_.append(object)
    return objects_

from dateable.chronos.browser.eventdisplay import EventDisplay
from zope.component import getAdapter

class SimpleCalendar(BaseContent, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()
    implements(ICalendarEnhanced, IPossibleCalendar, IEventProvider)

    meta_type = 'SimpleCalendar'
    _at_rename_after_creation = True

    schema = SimpleCalendar_schema

    ##code-section class-header #fill in your manual code here
    exclude_from_nav = True    
    ##/code-section class-header

    def getEvents(self, start, stop, EventDisplay=EventDisplay, **kw):
        result = list(map(lambda x: getAdapter(x.getObject(), IEvent,
                          'CalendarEventAdapter',),
                          self.portal_catalog(
                    start={'query':start, 'range':'min'},
                    end={'query':stop, 'range':'max'}, meta_type='ATEvent')))
        return result

    getOccurrences = getEvents

registerType(SimpleCalendar, PROJECTNAME)
# end of class SimpleCalendar

##code-section module-footer #fill in your manual code here
##/code-section module-footer



