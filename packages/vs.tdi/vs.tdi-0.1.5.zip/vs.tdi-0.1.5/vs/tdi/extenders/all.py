################################################################
# vs.tdi
# (C) 2012, Veit Schiele communications GmbH
# Author: Andreas Jung, ZOPYX Ltd
################################################################

from zope.interface import implements
from zope.component import adapts 
from Products.Archetypes import atapi
from Products.ATContentTypes.interfaces import IATContentType, IATFile
from Products.ATContentTypes import ATCTMessageFactory as _
from Products.CMFCore.utils import getToolByName
from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.field import ExtensionField

class StringField(ExtensionField, atapi.StringField):
    """ string field """

class All(object):
    adapts(IATContentType)
    implements(ISchemaExtender)

    fields = [StringField('tabText',
                         default='',
                         storage = atapi.AnnotationStorage(migrate=True),
                         widget=atapi.StringWidget(
                            size=20,
                            maxlength=20,
                            label=_(u'label_alternative_tab_text', u'Optional tab text'),
                         )
                    )
            ] 

    def __init__(self, context):
        self.context = context

    def getFields(self):
        qi = getToolByName(self.context, 'portal_quickinstaller')
        installedProducts = qi.listInstalledProducts()
        ids = [p['id'] for p in qi.listInstalledProducts()]
        if 'vs.tdi' in ids:
            return self.fields
        return ()


