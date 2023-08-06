from zope import schema
from zope.interface import Interface
from wildcard.pdfpal import mf as _
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

class IPDFPalLayer(Interface):
    """
    package layer
    """

class ILayer(Interface):
    """
    old package layer for compatibility issue
    """

class IPDFSettings(Interface):
    """
    PDF Settings
    """

    pdf_thumbnails_available = schema.Bool(
        title=u'Thumbnails available',
        default=False
    )

class IPDFPalConfiguration(Interface):
    """
    control panel config...
    """

    ocr_enabled = schema.Bool(
        title=_(u'OCR Enabled'),
        description=_(u'Enable this if you would like to use OCR for pdf document search results.'),
        required=True,
        default=True
    )

    overwrite_pdf_with_searchable_version = schema.Bool(
        title=_(u'Overwrite PDF with searchable version'),
        description=_(u"Overwrite the original PDF with an OCR version created during the OCR process(must be used along with 'OCR Enabled' option). "
                      u"**only available if you have tesseract(version 3.0.1 or greater), pdftk and hocr2pdf(part of exactimage package) installed."),
        default=True
    )

    thumbnail_gen_enabled = schema.Bool(
        title=_(u'PDF Thumbnails enabled'),
        required=True,
        default=False
    )

    preview_width = schema.Int(
        title=_(u'Preview Width'),
        required=True,
        default=512,
    )

    preview_height = schema.Int(
        title=_(u'Preview Height'),
        required=True,
        default=512,
    )

    thumbnail_width = schema.Int(
        title=_(u'Thumbnail Width'),
        required=True,
        default=128,
    )

    thumbnail_height = schema.Int(
        title=_(u'Thumbnail Height'),
        required=True,
        default=128,
    )

    split_large_pdfs = schema.Int(
        title=_(u'Split Large PDFs'),
        description=_(u'Sometimes PDFs do not convert well when they are very large. '
                      u'This allows you to split the PDF up before conversion so the pdf '
                      u'libraries do not have any issues. 0 means that PDFs will not be split. '
                      u'Otherwise, specify a size you would like to split on(400 recommended).'),
        required=True,
        default=0
    )

    fix_metadata = schema.Bool(
        title=u'Fix Metadata',
        description=u'Overwrite author with the site title and title with the title of the object',
        default=True
    )
