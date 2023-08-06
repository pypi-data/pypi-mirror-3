"""
This code has highly copied after the was pdfpeek does it.
"""

import logging
import cStringIO
from PIL import Image
from Products.Archetypes.atapi import FileField, AnnotationStorage
from settings import PDFPalConfiguration, PDFSettings
from Products.Archetypes.BaseUnit import BaseUnit
from commandrunner import command_subprocess
from DateTime import DateTime
import tempfile
import os

logger = logging.getLogger('wildcard.pdfpal')

preview_field = FileField('_preview_image', storage = AnnotationStorage(migrate=True))
thumb_field = FileField('_thumb_image', storage = AnnotationStorage(migrate=True))



class ghostscript_subprocess(command_subprocess):
    bin_name = 'gs'

    options = [
        "-sDEVICE=jpeg",
        "-dJPEGQ=99",
        "-dGraphicsAlphaBits=4",
        "-dTextAlphaBits=4",
        "-dDOINTERPOLATE",
        "-dSAFER",
        "-dBATCH",
        "-dNOPAUSE",
        "-dFirstPage=1",
        "-dLastPage=1",
        "-r59x56",
        "-sOutputFile=%(output)s",
        "-"
        ]

    def convert(self, filedata):
        _, filename = tempfile.mkstemp()
        process, output = self.run_command(stdin=filedata, opt_values={'output' : filename})
        return_code = process.returncode
        if return_code == 0:
            fi = open(filename)
            data = fi.read()
            fi.close()
            os.remove(filename)
            return data
        else:
            return None

try:
    ghostscript = ghostscript_subprocess()
except IOError:
    logger.exception("No GhostScript installed. PDF Pal will not be able to create thumbnails.")
    ghostscript = None

try:
    import plone.app.blob
    from ZODB.blob import Blob
    has_pab = True
except:
    has_pab = False

def create_thumbnails(context):
    """
    Creates Thumbnails for PDF
    """
    settings = PDFSettings(context)
    if not DateTime(settings.thumb_gen_last_updated) < DateTime(context.ModificationDate()):
        return # skip out if already done
        
    config = PDFPalConfiguration(context)
    preview_size = (config.preview_width, config.preview_height)
    thumb_size = (config.thumbnail_width, config.thumbnail_height)
    
    # create a file object to store the thumbnail and preview in
    raw_image_thumb = cStringIO.StringIO()
    raw_image_preview = cStringIO.StringIO()
    
    data = str(context.getFile().data)
    
    # run ghostscript, convert pdf page into image
    raw_image = ghostscript.convert(data)
    if not raw_image:
        return
    
    # use PIL to generate thumbnail from jpeg
    img_thumb = Image.open(cStringIO.StringIO(raw_image))
    img_thumb.thumbnail(thumb_size, Image.ANTIALIAS)
    # save the resulting thumbnail in the file object
    img_thumb.save(raw_image_thumb, "JPEG")
    # use PIL to generate preview from jpeg
    img_preview = Image.open(cStringIO.StringIO(raw_image))
    img_preview.thumbnail(preview_size, Image.ANTIALIAS)
    # save the resulting thumbnail in the file object
    img_preview.save(raw_image_preview, "JPEG")
    
    import transaction
    transaction.begin()
    settings = PDFSettings(context)
    if has_pab:
        blob = Blob()
        raw_image_preview.seek(0)
        blob.open('w').writelines(raw_image_preview.read())
        settings.preview_data = blob
        
        blob = Blob()
        raw_image_thumb.seek(0)
        blob.open('w').writelines(raw_image_thumb.read())
        settings.thumb_data = blob
    else:
        file = BaseUnit('_preview_image', raw_image_preview, 
            mimetype='image/jpeg',
            filename=context.getFilename().replace('.pdf', '_preview.jpg'),
            context=context)
        preview_field.set(context, file, _initializing_=True)
        file = BaseUnit('_thumb_image', raw_image_thumb, 
            mimetype='image/jpeg',
            filename=context.getFilename().replace('.pdf', '_thumb.jpg'),
            context=context)
        thumb_field.set(context, file, _initializing_=True)
        
    settings.pdf_thumbnails_available = True
    settings.thumb_gen_last_updated = DateTime().ISO8601()
    transaction.commit()
    
    logger.info("Thumbnails generated.")

