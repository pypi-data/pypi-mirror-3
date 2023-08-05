# -*- coding: utf-8 -*-

from zope.interface import Interface
from Products.ATContentTypes.interface.event import IATEvent

class IMonetEvent(IATEvent):
    """A recurring event"""
    
class IMonetCalendar(Interface):
    """Identifies objects on which you can use the calendar feature"""
    
class IMonetEventLayer(Interface):
    """Marker interface for monet.calendar.event layer"""