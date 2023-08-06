from Products.CMFCore.utils import getToolByName

types_to_add = [
    'Folder',
    'Large Plone Folder',
    'Plone Site'
]

def install(context):
    if not context.readDataFile('wildcard.pdfpal.install.txt'):
        return
    
    portal = context.getSite()
    types = getToolByName(portal, 'portal_types')
    
    for portal_type in types_to_add:
        if portal_type in types.objectIds():
            _type = types[portal_type]
            methods = list(_type.view_methods)
            methods.append('pdf-album-view')
            _type.view_methods = tuple(set(methods))
                
def uninstall(context):
    if not context.readDataFile('wildcard.pdfpal.uninstall.txt'):
        return

    portal = context.getSite()
    types = getToolByName(portal, 'portal_types')

    for portal_type in types_to_add:
        if portal_type in types.objectIds():
            _type = types[portal_type]
            methods = list(_type.view_methods)
            methods.remove('pdf-album-view')
            _type.view_methods = tuple(methods)