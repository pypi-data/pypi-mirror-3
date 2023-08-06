from zope.app.component.hooks import getSite
from zope.annotation.interfaces import IAnnotations
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.interface.file import IFileContent


def uninstall(context, reinstall=False):
    if not reinstall:
        setup = getToolByName(context, 'portal_setup')
        setup.runAllImportStepsFromProfile(
            'profile-wildcard.pdfpal:uninstall')

        portal = getSite()
        portal_actions = getToolByName(portal, 'portal_actions')
        object_buttons = portal_actions.object

        # remove actions
        actions_to_remove = ('pdfpal_index_document',)
        for action in actions_to_remove:
            if action in object_buttons.objectIds():
                object_buttons.manage_delObjects([action])

        catalog = getToolByName(portal, 'portal_catalog')
        objs = catalog(object_provides=IFileContent.__identifier__)

        # remove annotations and reset view
        for obj in objs:
            obj = obj.getObject()
            annotations = IAnnotations(obj)
            data = annotations.get('wildcard.pdfpal', None)
            if data:
                del annotations['wildcard.pdfpal']

        # remove control panel
        pcp = getToolByName(context, 'portal_controlpanel')
        pcp.unregisterConfiglet('pdf-pal')
