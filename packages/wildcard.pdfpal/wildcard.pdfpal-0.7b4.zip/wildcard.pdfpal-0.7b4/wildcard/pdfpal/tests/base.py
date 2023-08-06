import unittest2 as unittest
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import login
from zope.configuration import xmlconfig
from plone.app.testing.layers import FunctionalTesting
from plone.testing import z2
import os

_dir_path = os.path.dirname(__file__)
_pdf_filepath = os.path.join(_dir_path, 'testpdf.pdf')

class FakeSubProcess(object):
    runs = []
    return_data = None
    _run_command = None
    
    def __init__(self, return_data=None, process=None, run_command=None):
        self.runs = []
        self.return_data = return_data
        self.process = process
        self._run_command = run_command
    
    def run_command(self, **kw):
        self.runs.append(kw)
        if self._run_command:
            return self._run_command(**kw)
        else:
            return self.process, self.return_data

class Pal(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # load ZCML
        import wildcard.pdfpal
        xmlconfig.file('configure.zcml', wildcard.pdfpal,
                       context=configurationContext)
        z2.installProduct(app, 'wildcard.pdfpal')

    def setUpPloneSite(self, portal):
        # install into the Plone site
        applyProfile(portal, 'wildcard.pdfpal:default')

        # create admin user
        # z2.setRoles(portal, TEST_USER_NAME, ['Manager']) does not work
        # setRoles(portal, TEST_USER_NAME, ['Manager']) is not working either
        portal.acl_users.userFolderAddUser('admin',
                                           'secret',
                                           ['Manager'],
                                           [])
        login(portal, 'admin')

        # enable workflow for browser tests
        workflow = portal.portal_workflow
        workflow.setDefaultChain('plone_workflow')


PAL_FIXTURE = Pal()

PAL_FUNCTIONAL_TESTING = FunctionalTesting(bases=(PAL_FIXTURE,), name="PAL:Functional")


class PalTestCase(unittest.TestCase):

    layer = PAL_FUNCTIONAL_TESTING  
    
    pdf = open(_pdf_filepath)
    
    def createPDF(self, id="pdf", folder=None, **kw):
        if folder is None:
            folder = self.layer['portal']
        folder.invokeFactory("File", id, file=self.pdf, **kw)
        return folder[id]