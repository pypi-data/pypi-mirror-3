################################################################
# vs.contentnavigation
# (C) 2011, Veit Schiele Communications GmbH
################################################################

from zope.interface import implements
from zope.component import adapts
from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.field import ExtensionField
from Products.ATContentTypes.interfaces import IATFolder
from Products.Archetypes import atapi
from .. import contentnavigationMessageFactory as _

class MyBooleanField(ExtensionField, atapi.BooleanField):
    """ image field """

class FolderExtender(object):
    """ Folder fields """

    adapts(IATFolder)
    implements(ISchemaExtender)

    fields = [MyBooleanField('contentNavigation',
                           default=False,
                           widget=atapi.BooleanWidget(
                               label=_('label_display_subnavigation', 'Display subnavigation in content area')
                               ),  
                           ),  
            ] 

    def __init__(self, context):
        self.context = context

    def getFields(self):
        try:
            ids = [d['id'] for d in self.context.portal_quickinstaller.listInstalledProducts()]
        except AttributeError:
            return ()
        if 'vs.contentnavigation' in ids:
            return self.fields
        return ()

