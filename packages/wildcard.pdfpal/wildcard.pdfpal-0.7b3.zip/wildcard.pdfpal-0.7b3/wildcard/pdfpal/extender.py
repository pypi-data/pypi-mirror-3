from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from Products.ATContentTypes.interface import IFileContent
from interfaces import IPDFPalLayer
from archetypes.schemaextender.field import ExtensionField
from Products.Archetypes.atapi import TextField, TextAreaWidget
from zope.component import adapts
from zope.interface import implements

class ExtensionTextField(ExtensionField, TextField):
    """ derivative of textfield for extending schemas """

class FileOCRExtender(object):
    adapts(IFileContent)
    implements(IBrowserLayerAwareExtender)

    layer = IPDFPalLayer

    fields = [
        ExtensionTextField('ocrText',
            required = False,
            searchable = True,
            default = '',
            widget = TextAreaWidget(
                label="Text from OCR",
                description="Text from PDF documents using OCR",
                visible = {"edit": "invisible", "view": "invisible"},
            )
        )
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields
