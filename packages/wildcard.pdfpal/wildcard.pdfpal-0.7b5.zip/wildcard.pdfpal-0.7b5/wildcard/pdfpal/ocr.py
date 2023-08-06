import logging
from settings import PDFSettings
from DateTime import DateTime
import os
import tempfile
import shutil
from Products.CMFCore.utils import getToolByName
from settings import PDFPalConfiguration
from hashlib import md5
from lxml.cssselect import CSSSelector
from lxml.html import fromstring
from wildcard.pdfpal.commands import get_command, hocr_enabled

try:
    from wc.pageturner.events import queue_job
    from wc.pageturner.events import convert as pageturner_convert
    from wc.pageturner.events import handle_file_creation as pthandle_file_creation
    pageturner_installed = True
except:
    pageturner_installed = False

logger = logging.getLogger('wildcard.pdfpal.ocr')

_tiff_output_filename = 'image_%04d.tiff'
_pdf_output_filename = 'image_*.tiff.pdf'

def get_hash(data):
    m = md5()
    m.update(data)
    return m.digest()

_paragraph_selector = CSSSelector('p.ocr_par')
_line_selector = CSSSelector('span.ocr_line')
_text_selector = CSSSelector('span.xocr_word')
def extract_ocr_text_from_hocr_file(html):
    xml = fromstring(html)
    result = ''
    for paragraph in _paragraph_selector(xml):
        for line in _line_selector(paragraph):
            result += '\n'
            for word in _text_selector(line):
                result += ' ' + word.text_content()

    return result

def read_file(filepath):
    if os.path.exists(filepath):
        fi = open(filepath)
        data = fi.read()
        fi.close()
        return data
    else:
        return ''

def remove_file(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)

def split_pdf(context, start, end, orig_filename, input_filename, metadata_filename, result_directory):
    field = context.getField('file')
    _, tmpfile = tempfile.mkstemp()
    new_pdffilename = os.path.join(result_directory, orig_filename + ' pages %d-%d.pdf' % (start, end))

    pdftk_split = get_command('pdftk_split')
    copyPdfMetadata = get_command('copyPdfMetadata')
    process, output = pdftk_split.run_command(opt_values={'start' : start, 'end' : end, 'input' : input_filename, 'output' : tmpfile})
    process, output = copyPdfMetadata.run_command(opt_values={'info_file' : metadata_filename, 'input': tmpfile, 'output' : new_pdffilename})
    pdf = open(new_pdffilename)
    field.set(context, pdf)
    pdf.close()
    context.setTitle(context.Title() + ' pages(%d-%d)' % (start, end))

    remove_file(tmpfile)
    remove_file(new_pdffilename)

def create_file(container, id, title):
    container.invokeFactory(type_name="File", id=id, title=title)
    obj = container[id]
    return obj

def _handle_file_creation(obj):
    #if pageturner_installed:
    #    pthandle_file_creation(obj, None)
    from wildcard.pdfpal.events import handle_file_creation
    handle_file_creation(obj, None)

def index_pdf(context):
    """
    Index PDF using OCR
    """
    settings = PDFSettings(context)
    if not DateTime(settings.ocr_last_updated) < DateTime(context.ModificationDate()):
        logger.info("File already OCR'd since last modification: %s" % context.getId())
        return # skip out if already done...

    filedata = str(context.getFile().data)
    filehash = get_hash(filedata)
    if settings.file_hash == filehash:
        logger.info('file hash matches. Skipping OCR for %s' % context.getId())
        return

    result_directory = tempfile.mkdtemp()
    output_path = os.path.join(result_directory, _tiff_output_filename)
    text_path = os.path.join(result_directory, 'output')
    textfilepath = os.path.join(result_directory, 'output.txt')
    hocrfilepath = os.path.join(result_directory, 'output.html')
    pdfinfo_filepath = os.path.join(result_directory, 'pdf_info.txt')
    configuration = PDFPalConfiguration(context)
    pdftk_split = get_command('pdftk_split')
    if configuration.split_large_pdfs and pdftk_split:
        _, filename = tempfile.mkstemp()
        fi = open(filename, 'w')
        fi.write(filedata)
        fi.close()
        pdftk_numpage = get_command('pdftk_numpage')
        numpages = pdftk_numpage.numpages(opt_values={'filename' : filename})
        if numpages > configuration.split_large_pdfs:
            field = context.getField('file')
            title = context.Title()
            orig_filename, ext = os.path.splitext(field.getFilename(context))
            dumpPdfMetadata = get_command('dumpPdfMetadata')
            dumpPdfMetadata.run_command(stdin=filedata, opt_values={'output' : pdfinfo_filepath})
            split_pdf(context, 1, configuration.split_large_pdfs-1, orig_filename, filename, pdfinfo_filepath, result_directory)
            context.reindexObject()
            _handle_file_creation(context)

            container = context.getParentNode()
            pdfnumber = 0
            for pdfnumber in range(1, numpages/configuration.split_large_pdfs):
                # convert
                obj = create_file(container, context.getId() + '-' + str(pdfnumber), title)
                start = pdfnumber*configuration.split_large_pdfs
                end = start+configuration.split_large_pdfs-1
                split_pdf(obj, start, end, orig_filename, filename, pdfinfo_filepath, result_directory)
                obj.reindexObject()
                _handle_file_creation(obj)

            #do remainder now.
            obj = create_file(container, context.getId() + '-' + str(pdfnumber+1), title)
            start = (pdfnumber*configuration.split_large_pdfs)+configuration.split_large_pdfs
            end = start+(numpages%configuration.split_large_pdfs)-1
            split_pdf(obj, start, end, orig_filename, filename, pdfinfo_filepath, result_directory)
            obj.reindexObject()
            _handle_file_creation(obj)
            return

    ghostscript = get_command('ghostscript')
    process, output = ghostscript.run_command(stdin=filedata, opt_values={'outputfilename' : output_path})

    files = os.listdir(result_directory)
    files.sort()
    txtoutput = ''
    try:
        for tif in files:
            path = os.path.join(result_directory, tif)

            tesseract = get_command('tesseract')
            process, output = tesseract.run_command(opt_values={'imagefilename' : path, 'txtfilename' : text_path})
            if hocr_enabled:
                hocrdata = read_file(hocrfilepath)
                remove_file(hocrfilepath)
                if configuration.overwrite_pdf_with_searchable_version:
                    opts = {'input' : path, 'output' : path + '.pdf'}
                    if hocrdata:
                        hocr2pdf = get_command('hocr2pdf')
                        hocr2pdf.run_command(opt_values=opts, stdin=hocrdata)
                    else:
                        tiff2pdf = get_command('tiff2pdf')
                        tiff2pdf.run_command(opt_values=opts)

                if hocrdata:
                    txt = extract_ocr_text_from_hocr_file(hocrdata)
                else:
                    txt = ''
            else:
                txt = read_file(textfilepath)
                remove_file(textfilepath)

            txtoutput += '\n' + txt
            os.remove(path)
    except:
        logger.exception("There was an error running OCR for %s" % context.getId())

    if configuration.overwrite_pdf_with_searchable_version and hocr_enabled:
        # now combine the new pdf
        field = context.getField('file')
        orig_filename = field.getFilename(context)
        _, tmpfile = tempfile.mkstemp()
        new_pdffilename = os.path.join(result_directory, orig_filename)
        try:
            combinePDFs = get_command('combinePDFs')
            process, output = combinePDFs.run_command(opt_values={
                'input_files' : os.path.join(result_directory, _pdf_output_filename),
                'output' : tmpfile
            })
            _, tmpfile2 = tempfile.mkstemp()
            get_command('optimize').run_command(opt_values={'output' : tmpfile2, 'input' : tmpfile})
            get_command('dumpPdfMetadata').run_command(stdin=filedata, opt_values={'output' : pdfinfo_filepath})
            if configuration.fix_metadata:
                portal = getToolByName(context, 'portal_url').getPortalObject()
                site_title = portal.Title()
                info =''
                file = open(pdfinfo_filepath)
                last_line = None
                for line in file.readlines():
                    if last_line == 'InfoKey: Creator':
                        info += 'InfoValue: %s\n' % site_title
                    elif last_line == 'InfoKey: Title':
                        info += 'InfoValue: %s\n' % context.Title()
                    elif last_line == 'InfoKey: Author':
                        info += 'InfoValue: %s\n' % site_title
                    else:
                        info += line
                    last_line = line.strip()
                file.close()
                file = open(pdfinfo_filepath, 'w')
                file.write(info)
                file.close()

            process, output = get_command('copyPdfMetadata').run_command(opt_values={'info_file' : pdfinfo_filepath, 'input': tmpfile2, 'output' : new_pdffilename})
            pdf = open(new_pdffilename)
            import transaction
            transaction.begin()
            field.set(context, pdf)
            filehash = get_hash(pdf.read())
            pdf.close()
            transaction.commit()
        except:
            logger.exception("There was an error making the PDF '%s' searchable " % context.getId())

    # Clean-up temp dir
    shutil.rmtree(result_directory)

    import transaction
    transaction.begin()
    if txtoutput:
        field = context.getField('ocrText')
        field.set(context, txtoutput)
        context.reindexObject(idxs=['SearchableText'])

    context.setModificationDate(DateTime())
    settings.ocr_last_updated = DateTime().ISO8601()
    settings.file_hash = filehash
    transaction.commit()

    qi = getToolByName(context, 'portal_quickinstaller')
    if pageturner_installed and qi.isProductInstalled('wc.pageturner'):
        # When both products are installed at the same time, page turner defers to
        # pdfpal to convert the pdf first so it can create the correct flexpaper
        pageturner_convert(context)

