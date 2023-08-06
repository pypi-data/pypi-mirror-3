from Products.Five import BrowserView
from zope.component import getUtility
from Products.CMFPlone.utils import base_hasattr
from Products.Archetypes.utils import contentDispositionHeader
from os import fstat
from webdav.common import rfc1123_date
from wildcard.pdfpal.thumbnail import preview_field, thumb_field
from wildcard.pdfpal import mf as _
from wildcard.pdfpal.interfaces import IPDFPalConfiguration
from plone.app.controlpanel.form import ControlPanelForm
from zope.formlib import form
from Products.CMFCore.utils import getToolByName
from wildcard.pdfpal.events import handle_file_creation
from DateTime import DateTime
from wildcard.pdfpal.settings import PDFSettings
from Products.ATContentTypes.interface.file import IFileContent

def time_since(dt):
    now = DateTime('UTC')
    diff = now - dt
    
    secs = int(diff*24*60*60)
    minutes = secs/60
    hours = minutes/60
    days = hours/24
    
    if days:
        return '%i day%s' % (days, days > 1 and 's' or '')
    elif hours:
        return '%i hour%s' % (hours, hours > 1 and 's' or '')
    elif minutes:
        return '%i minute%s' % (minutes, minutes > 1 and 's' or '')
    else:
        return '%i second%s' % (secs, secs > 1 and 's' or '')


try:
    from plone.app.async.interfaces import IAsyncService
    paa_installed = True
except:
    paa_installed = False

class AsyncMonitor(BrowserView):
    """
    
    """
    
    def get_job_data(self, job):
        lastused = DateTime(job._p_mtime)
        if job.status != 'pending-status':
            timerunning = time_since(lastused)
        else:
            timerunning = '-'
        return {
            'status' : job.status,
            'user' : job.args[3],
            'object_path' : '/'.join(job.args[0]),
            'description' : getattr(job.args[4], '__doc__', job.args[4].__name__).strip(),
            'lastused' : lastused.toZone('UTC').pCommon(),
            'timerunning' : timerunning
        }
    
    @property
    def jobs(self):
        results = []
        
        if paa_installed:
            async = getUtility(IAsyncService)
            queue = async.getQueues()['']
        
            for quota in queue.quotas.values():
                for job in quota._data:
                    results.append(self.get_job_data(job))        
        
            jobs = [job for job in queue]
            for job in jobs:
                results.append(self.get_job_data(job))
            
        return results
        
        
class AlbumView(BrowserView):
    
    def getContents(self, object=None, portal_type=('File',), full_objects=False, path=None):
        if not object:
            object = self.context
            
        opts = { 'portal_type' : portal_type }
        if path:
            opts['path'] = path
            
        if object.portal_type == 'Topic':
            res = object.queryCatalog(**opts)
        else:
            opts['sort_on'] = 'getObjPositionInParent'
            res = object.getFolderContents(contentFilter = opts, full_objects=full_objects)
        
        return res
    
    def results(self):

        result = {}

        result['files'] = self.getContents(portal_type=('File',), full_objects=True)
        result['folders'] = self.getContents(portal_type = ('Folder', 'Large Plone Folder'))

        return result
        
        
    def get_files(self, obj):
        #Handle brains or objects
        if base_hasattr(obj, 'getPath'):
            path = obj.getPath()
        else:
            path = '/'.join(obj.getPhysicalPath())
        # Explicitly set path to remove default depth
        return self.getContents(object=obj, portal_type = ('File',), path = path)
        
        
try:
    import plone.app.blob
    from plone.app.blob.download import handleRequestRange
    from plone.app.blob.iterators import BlobStreamIterator
    from plone.app.blob.utils import openBlob
    from ZODB.blob import Blob
    has_pab = True
except:
    has_pab = False
        
class PDFPreviewImageView(BrowserView):
    
    image_type = 'preview'
    field = preview_field
    
    def render_blob_version(self, blob):
        # done much like it is done in plone.app.blob's index_html
        header_value = contentDispositionHeader(disposition='attachment', filename='image_%s.jpg' % self.image_type)
        
        blobfi = openBlob(blob)
        length = fstat(blobfi.fileno()).st_size
        blobfi.close()
        
        self.request.response.setHeader('Last-Modified', rfc1123_date(self.context._p_mtime))
        self.request.response.setHeader('Accept-Ranges', 'bytes')
        self.request.response.setHeader('Content-Disposition', header_value)
        self.request.response.setHeader("Content-Length", length)
        self.request.response.setHeader('Content-Type', 'image/jpeg')
        range = handleRequestRange(self.context, length, self.request, self.request.response)
        return BlobStreamIterator(blob, **range)
        
    def __call__(self):
        settings = PDFSettings(self.context)
        blob = getattr(settings, self.image_type + '_data', None)
        if has_pab and isinstance(blob, Blob):
            return self.render_blob_version(blob)
        else:
            try:
                return self.field.download(self.context)
            except:
                return ''
            
class PDFThumbImageView(PDFPreviewImageView):

    image_type = 'thumb'
    field = thumb_field
    
    
class PDFPalControlPanel(ControlPanelForm):
    """Control panel form for setting pdfpeek image and thumbnail sizes"""
    form_fields = form.FormFields(IPDFPalConfiguration)
    label = _(u'PDF Pal Settings')
    description = _(u'Manage PDF Pal settings')
    form_name = _(u'PDF Pal Settings')


class QueuePDFs(BrowserView):
    
    def __call__(self):
        confirm = self.request.get('confirm', False)
        if confirm == 'yes':
            catalog = getToolByName(self.context, 'portal_catalog')
            files = catalog(portal_type=('File',))
            for brain in files:
                fi = brain.getObject()
                handle_file_creation(fi, None)
            return 'All files queued.'
        else:
            return 'You must confirm you want to actually do this. Append `?confirm=yes` onto the url.'
            
class ManualTrigger(BrowserView):
    
    def __call__(self):
        palsettings = PDFSettings(self.context)
        palsettings.ocr_last_updated = DateTime('1999/01/01').ISO8601()
        palsettings.file_hash = None
        try:
            from wc.pageturner.settings import Settings as PTSettings
            ptsettings = PTSettings(self.context)
            ptsettings.last_updated = DateTime('1999/01/01').ISO8601()
        except:
            pass
        handle_file_creation(self.context, None)
        self.request.response.redirect(self.context.absolute_url() + '/view')
        
class Utilities(BrowserView):
    
    def is_pdf(self, context=None):
        if context is None:
            context = self.context
            
        if IFileContent.providedBy(context) and hasattr(context, 'getContentType'):
            return context.getContentType() in ('application/pdf', 'application/x-pdf', 'image/pdf')
        else:
            return False
            