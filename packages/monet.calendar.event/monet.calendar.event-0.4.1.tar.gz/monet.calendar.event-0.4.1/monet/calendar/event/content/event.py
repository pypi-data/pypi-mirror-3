"""Definition of the Event content type
"""

from zope.interface import implements #, directlyProvides

try:
    # turn off
    from Products.LinguaPlone.public import *
except ImportError:
    # No multilingual support
    from Products.Archetypes.atapi import *

from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from monet.calendar.event import eventMessageFactory as _
from monet.calendar.event.interfaces import IMonetEvent, IMonetCalendar
from monet.calendar.event.config import PROJECTNAME

from monet.calendar.event.content.base_recurring_event import EventSchema as RecurringEventSchema
from monet.calendar.event.content.base_recurring_event import RecurringEvent

from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.atapi import DisplayList
from Products.ATContentTypes.content.image import ATImageSchema
from Products.ATContentTypes.lib.imagetransform import ATCTImageTransform
from Products.ATContentTypes.permission import ChangeEvents
from Products.ATContentTypes.configuration import zconf
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View

EventSchema = RecurringEventSchema.copy() + Schema((

    LinesField('eventType',
               required=True,
               searchable=False,
               languageIndependent=True,
               enforceVocabulary=True,
               vocabulary='getEventTypeVocab',
               widget = MultiSelectionWidget(
                        format = 'checkbox',
                        label = _(u'label_event_type', default=u'Event Type(s)')
                        )),
    
    StringField('slots',
                required=True,
                searchable=False,
                languageIndependent=True,
                vocabulary='getSlotsVocab',
                default='',
                widget=SelectionWidget(
                        format = 'select',
                        label = _(u'label_slots', default=u'Time slots'),
                        description = _(u'help_slots', default=u'Select the time of day on which the event takes place.')
                        )),
                        
    TextField('time',
              required=True,
              searchable=False,
              storage = AnnotationStorage(migrate=True),
              validators = ('isTidyHtmlWithCleanup',),
              default_output_type = 'text/x-html-safe',
              widget = RichWidget(
                        label = _(u'label_time', default=u'Hours'),
                        description = _(u'help_time', default=u'Indicate the time of the event. Use a key combination shift + enter to wrap (not just enter)'),
                        rows = 25,
                        allow_file_upload = zconf.ATDocument.allow_document_upload
                        )),
                        
    TextField('cost',
                required=False,
                searchable=False,
                widget=TextAreaWidget(
                        label = _(u'label_cost', default=u'Entrance fee'),
                        description = _(u'help_cost', default=u'Indicate whether the event is free or not (in this case indicate the cost and any reductions/discounts).'),
                        rows=3,
                        )),
    
    TextField('location',
               required=False,
               searchable=False,
               write_permission = ChangeEvents,
               widget=TextAreaWidget(
                        label = _(u'label_location', default=u'Where'),
                        rows=2,
                        )),       
    
    StringField('address',
                required=True,
                searchable=False,
                languageIndependent=True,
                widget=StringWidget(
                        label = _(u'label_address', default=u'Address'),
                        size=80
                        )),
                        
    StringField('country',
                required=False,
                searchable=False,
                languageIndependent=True,
                widget=StringWidget(
                        label = _(u'label_country', default=u'Nation'),
                        size=40
                        )),
                        
    StringField('zipcode',
                required=False,
                searchable=False,
                languageIndependent=True,
                validators=("isInt"),
                widget=StringWidget(
                        label = _(u'label_zipcode', default=u'ZIP code'),
                        size=20
                        )),
                                            
    LinesField('contactPhone',
                required=False,
                searchable=False,
                accessor='contact_phone',
                write_permission = ChangeEvents,
                languageIndependent=True,
                widget=LinesWidget(
                        label = _(u'label_contactPhone',default=u'Telephone'),
                        cols = 50,
                        )),

    StringField('fax',
                required=False,
                searchable=False,
                languageIndependent=True,
                widget=StringWidget(
                        label = _(u'label_fax', default=u'Fax'),
                        size= 45,
                        )),
                        
    LinesField('eventUrl',
                required=False,
                searchable=False,
                accessor='event_url',
                write_permission = ChangeEvents,
                languageIndependent = True,
                widget = LinesWidget(
                        description = '',
                        label = _(u'label_eventUrl',default=u'Web site'),
                        cols = 60,
                        )),
                        
    LinesField('contactEmail',
                required=False,
                searchable=False,
                accessor='contact_email',
                write_permission = ChangeEvents,
                languageIndependent = True,
                widget = LinesWidget(
                        description = '',
                        label = _(u'label_contactEmail',default=u'E-mail'),
                        cols = 40,
                        )),

    LinesField('referenceEntities',
               required=False,
               searchable=False,
               widget=LinesWidget(
                        label = _(u'label_referenceentities', default=u'Reference organization'),
                        )),
                        
    TextField('annotations',
              required=False,
              searchable=False,
              storage = AnnotationStorage(migrate=True),
              validators = ('isTidyHtmlWithCleanup',),
              default_output_type = 'text/x-html-safe',
              read_permission=permissions.ModifyPortalContent,
              widget = RichWidget(
                        label = _(u'label_annotations', default=u'Annotations'),
                        description = _(u'help_annotations', default=u"Enter here your notes about the event. This field is only for use by the operator and doesn't appear on the site."),
                        allow_file_upload = zconf.ATDocument.allow_document_upload
                        )),

    TextField('imageAlt',
               searchable=True,
               required=False,
               widget=TextAreaWidget(
                        label = _(u'label_imagealt', default=u'Image ALT text'),
                        description = _(u'help_imagealt', default=(u'If the image is significant for understanding the event, '
                                                                   u'you must enter there the alternative text (ALT) for accessibility reason. '
                                                                   u'Keep this field empty if the image has only layout purpose.')),
                        )), 

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

EventSchema['title'].storage = AnnotationStorage()
EventSchema['description'].storage = AnnotationStorage()

EventSchema['description'].widget.description= _(u'help_description_event',default=u'A short description of the event')

schemata.finalizeATCTSchema(EventSchema, moveDiscussion=False)

EventSchema.moveField('eventType', after='description')

imageField = ATImageSchema['image'].copy()
imageField.required = False
imageField.primary = False
imageField.validators = None
imageField.languageIndependent= True
EventSchema.addField(imageField)
EventSchema.moveField('image', after='eventType')
EventSchema.moveField('imageAlt', after='image')

EventSchema['startDate'].widget.show_hm = False
EventSchema['startDate'].widget.label= _(u'label_startDate',default=u'From')
EventSchema['endDate'].widget.show_hm = False
EventSchema['endDate'].widget.label= _(u'label_endDate',default=u'To')
EventSchema.moveField('startDate', after='imageAlt')
EventSchema.moveField('endDate', after='startDate')

EventSchema.moveField('cadence', after='endDate')
EventSchema.moveField('except', after='cadence')
EventSchema.moveField('including', after='except')

EventSchema.moveField('slots', after='including')
EventSchema.moveField('time', after='slots')
EventSchema.moveField('cost', after='time')

#EventSchema['location'].widget.description = _(u'help_location',default=u'Enter the event location.')
EventSchema.changeSchemataForField('location', 'default')
EventSchema.moveField('location', after='cost')
EventSchema.moveField('address', after='location')
EventSchema.moveField('country', after='address')
EventSchema.moveField('zipcode', after='country')

EventSchema.moveField('contactPhone', after='zipcode')
EventSchema.moveField('fax', after='contactPhone')

EventSchema.moveField('eventUrl', after='fax')
EventSchema.moveField('contactEmail', after='eventUrl')

EventSchema['text'].widget.label = _(u'label_text',default=u'Event body text')
EventSchema['text'].widget.description = _(u'help_text',default=u'Enter all other information about the event.')
EventSchema.moveField('text', after='contactEmail')

EventSchema.moveField('referenceEntities', after='text')
EventSchema.moveField('annotations', after='referenceEntities')

EventSchema['attendees'].languageIndependent=True
EventSchema['attendees'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
EventSchema['contactName'].languageIndependent=True
EventSchema['contactName'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}

class MonetEvent(RecurringEvent, ATCTImageTransform):
    """Description of the Example Type"""
    implements(IMonetEvent, IMonetCalendar)

    meta_type = "ATEvent"
    schema = EventSchema

    title = ATFieldProperty('title')
    #description = ATFieldProperty('description')
    
    security = ClassSecurityInfo()
    
    def getEventTypeVocab(self):
        mp = getToolByName(self,'portal_properties')
        items = mp.monet_calendar_event_properties.event_types
        vocab = DisplayList()
        for item in items:
            vocab.add(item,_(item))
        return vocab
    
    def getSlotsVocab(self):
        vocab = DisplayList()
        vocab.add('',_(u'-- Unspecified --'))
        vocab.add('morning',_(u'Morning'))
        vocab.add('afternoon',_(u'Afternoon'))
        vocab.add('night',_(u'Evening'))
        vocab.add('allday',_(u'All day long'))
        return vocab
    
    security.declareProtected(View, 'tag')
    def tag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        return self.getField('image').tag(self, **kwargs)

    def __bobo_traverse__(self, REQUEST, name):
        """Transparent access to image scales
        """
        if name.startswith('image'):
            field = self.getField('image')
            image = None
            if name == 'image':
                image = field.getScale(self)
            else:
                scalename = name[len('image_'):]
                scalename.replace(".jpg", "")
                if scalename in field.getAvailableSizes(self):
                    image = field.getScale(self, scale=scalename)
            if image is not None and not isinstance(image, basestring):
                # image might be None or '' for empty images
                return image

        return base.ATCTContent.__bobo_traverse__(self, REQUEST, name)

registerType(MonetEvent, PROJECTNAME)
