from zope.component import getUtility
from logging import getLogger
from ocr import index_pdf
from thumbnail import create_thumbnails
from settings import PDFPalConfiguration
from Products.CMFCore.utils import getToolByName

logger = getLogger('wildcard.pdfpal')

try:
    from plone.app.async.interfaces import IAsyncService
    async_installed = True
except:
    async_installed = False

try:
    from wc.pageturner.events import queue_job as queue_pageturner_job
    pageturner_installed = True
except:
    pageturner_installed = False
def job_failure_callback(*args):
    pass


def handle_file_creation(object, event):
    qi = getToolByName(object, 'portal_quickinstaller')
    if qi.isProductInstalled('collective.documentviewer'):
        return
    if not qi.isProductInstalled('wildcard.pdfpal'):
        if pageturner_installed and qi.isProductInstalled('wc.pageturner'):
            # so pdfpal might not be installed, pageturner still might need 
            # get it's just queued up
            queue_pageturner_job(object)
        return
    if object.getContentType() not in ('application/pdf', 'application/x-pdf', 'image/pdf'):
        return

    config = PDFPalConfiguration(object)
        
    queued = False
    if async_installed:
        try:
            async = getUtility(IAsyncService)
            if config.ocr_enabled:
                job = async.queueJob(index_pdf, object)
            elif pageturner_installed and qi.isProductInstalled('wc.pageturner'):
                queue_pageturner_job(object)
            if config.thumbnail_gen_enabled:
                job = async.queueJob(create_thumbnails, object)
            queued = True
        except:
            logger.exception("Error using plone.app.async with wildcard.pdfpal. Converting pdf without plone.app.async...")
            
    if not queued: # using async didn't work. Do it manually.
        if config.ocr_enabled:
            index_pdf(object)
        elif pageturner_installed and qi.isProductInstalled('wc.pageturner'):
            # since this won't be done in wc.pageturner, fire it off here...
            queue_pageturner_job(object)
        if config.thumbnail_gen_enabled:
            create_thumbnails(object)
