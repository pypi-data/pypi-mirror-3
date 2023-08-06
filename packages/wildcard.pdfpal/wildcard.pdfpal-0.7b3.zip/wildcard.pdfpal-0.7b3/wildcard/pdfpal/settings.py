from zope.interface import implements
from interfaces import IPDFPalConfiguration, IPDFSettings
from Products.CMFCore.utils import getToolByName
from zope import schema
from zope.annotation.interfaces import IAnnotations
from DateTime import DateTime
from persistent.dict import PersistentDict
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapts


_prefix = "pdfpal_"

schema_type_mapping = {
    schema.TextLine : 'string',
    schema.Choice : 'string',
    schema.Bool : 'boolean',
    schema.Int : 'int'
}

class PDFPalConfiguration(object):
    implements(IPDFPalConfiguration)
    adapts(IPloneSiteRoot)
    
    def __init__(self, context):
        self.context = context
        self.pprops = getToolByName(context, 'portal_properties')
        self.site_props = getattr(self.pprops, 'site_properties', None)
                    
    def __setattr__(self, name, value):
        if name[0] == '_' or name in ['context', 'pprops', 'site_props']:
            self.__dict__[name] = value
        else:
            propname = _prefix + name
            if not self.site_props.hasProperty(propname):
                self.site_props.manage_addProperty(propname, value, schema_type_mapping[type(IPDFPalConfiguration[name])])
            
            self.site_props.manage_changeProperties(**{propname : value})

    def __getattr__(self, name):
        default = None
        if name in IPDFPalConfiguration.names():
            default = IPDFPalConfiguration[name].default
        
        propname = _prefix + name
        return self.site_props.getProperty(propname, default)


class PDFSettings(object):
    implements(IPDFSettings)

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(self.context)

        self._metadata = annotations.get('wildcard.pdfpal', None)
        if self._metadata is None:
            self._metadata = PersistentDict()
            self._metadata['ocr_last_updated'] = DateTime('1901/01/01').ISO8601()
            self._metadata['thumb_gen_last_updated'] = DateTime('1901/01/01').ISO8601()
            annotations['wildcard.pdfpal'] = self._metadata

    def __setattr__(self, name, value):
        if name[0] == '_' or name == 'context':
            self.__dict__[name] = value
        else:
            self._metadata[name] = value

    def __getattr__(self, name):
        default = None
        if name in IPDFSettings.names():
            default = IPDFSettings[name].default

        return self._metadata.get(name, default)
