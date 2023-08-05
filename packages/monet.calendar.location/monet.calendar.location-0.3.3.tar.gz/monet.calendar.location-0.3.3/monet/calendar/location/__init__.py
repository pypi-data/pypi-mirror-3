from monet.calendar.event.content.event import MonetEvent
from monet.calendar.event.config import PROJECTNAME
from Products.MasterSelectWidget.MasterSelectWidget import MasterSelectWidget
from redturtle.entiterritoriali import _all_regioni, _all_province, _all_comuni, EntiVocabulary
from redturtle.entiterritoriali.vocabulary import mapDisplayList
from Products.Archetypes.atapi import DisplayList
from Products.Archetypes import atapi

from zope.i18nmessageid import MessageFactory
_ = locationMessageFactory = MessageFactory('monet.calendar.location')

def monetVocabMap(list):
    result = [(u"",_(u'-- Unspecified --'))]
    return mapDisplayList(list, result)

REGIONI = DisplayList(monetVocabMap(_all_regioni))
PROVINCE = DisplayList(monetVocabMap(EntiVocabulary.province4regione("08")))
COMUNI = DisplayList(monetVocabMap(EntiVocabulary.comuni4provincia("MO")))

def getVocabProv(self,region):
    province = EntiVocabulary.province4regione(region)
    return DisplayList(monetVocabMap(province))
    
def getVocabMun(self,province):
    municipality = EntiVocabulary.comuni4provincia(province)
    return DisplayList(monetVocabMap(municipality))

LocationSchema = atapi.Schema((

    atapi.StringField('region',
                required=False,
                searchable=False,
                languageIndependent=True,
                default='08',
                vocabulary=REGIONI,
                widget=MasterSelectWidget(
                        label = _(u'label_region', default=u'Region'),
                        slave_fields = ({'name':'province',
                                         'action': 'vocabulary',
                                         'vocab_method': 'getVocabProvince',
                                         'control_param': 'region'},)
                        )),
                        
    atapi.StringField('province',
                required=False,
                searchable=False,
                languageIndependent=True,
                vocabulary=PROVINCE,
                default="MO",
                widget=MasterSelectWidget(
                        label = _(u'label_province', default=u'Province'),
                        slave_fields = ({'name':'municipality',
                                         'action': 'vocabulary',
                                         'vocab_method': 'getVocabMunicipality',
                                         'control_param': 'province'},)
                        )),
                        
    atapi.StringField('municipality',
                required=False,
                searchable=False,
                languageIndependent=True,
                vocabulary=COMUNI,
                default="036023",
                widget=atapi.SelectionWidget(
                        label = _(u'label_municipality', default=u'Location'),
                        format="select",
                        )),
                        
    atapi.StringField('locality',
                required=False,
                searchable=False,
                languageIndependent=True,
                widget=atapi.StringWidget(
                        label = _(u'label_locality', default=u'Locality'),
                        size = 50
                        )),
))

MonetEvent.schema += LocationSchema.copy()
MonetEvent.schema.moveField('region', after='country')
MonetEvent.schema.moveField('province', after='region')
MonetEvent.schema.moveField('municipality', after='province')
MonetEvent.schema.moveField('locality', after='municipality')
MonetEvent.schema.moveField('zipcode', after='locality')
MonetEvent.schema.moveField('contactPhone', after='zipcode')
MonetEvent.schema.moveField('fax', after='contactPhone')
MonetEvent.schema.moveField('eventUrl', after='fax')
MonetEvent.schema.moveField('contactEmail', after='eventUrl')
MonetEvent.schema.moveField('text', after='contactEmail')
MonetEvent.schema.moveField('referenceEntities', after='text')
MonetEvent.schema.moveField('annotations', after='referenceEntities')

MonetEvent.schema['country'].default = 'Italia'
MonetEvent.schema['eventType'].widget.macro = 'twocolumnsmultiselection'
MonetEvent.schema['relatedItems'].widget.description = _(u'help_relatedItems',default=u'Use to attach to the event its program, invitation card, etc...')
MonetEvent.schema['location'].widget.description = _(u'help_location',default=u"Enter the physical location where the event takes place (eg Novi Sad, Palazzina dei Giardini, etc.). Complete only if different from the address.")
MonetEvent.schema['referenceEntities'].widget.description = _(u'help_referenceentities', default=u'Indicate the promoters and organizers of the event. (eg: City of Modena, San Carlo Foundation, etc.).')

MonetEvent.getVocabProvince=getVocabProv
MonetEvent.getVocabMunicipality=getVocabMun

print "monet.calendar.location: Added fields region, province, municipality and locality to MonetEvent"

atapi.registerType(MonetEvent, PROJECTNAME)


def initialize(context):
    """Initializer called when used as a Zope 2 product."""

