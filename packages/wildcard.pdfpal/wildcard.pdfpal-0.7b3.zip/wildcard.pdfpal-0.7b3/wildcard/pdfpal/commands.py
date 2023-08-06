from commandrunner import command_subprocess
import logging
logger = logging.getLogger('wildcard.pdfpal')
from os import environ

OLD_TESSERACT_VERSION = environ.get('AUTHORIZE_OLD_TESSERACT_VERSION', '')
if OLD_TESSERACT_VERSION.lower() in ('true', 'on', '1'):
    OLD_TESSERACT_VERSION = True
    logger.info("Old Tesseract3 version will be authorized.")
else:
    OLD_TESSERACT_VERSION = False

_processes = {}

class ghostscript_subprocess(command_subprocess):
    bin_name = 'gs'

    logging = {
        'info' : "Converted PDF to tiff files.",
        'warn' : "Ghostscript process did not exit cleanly! Error Code: %(return_code)d"
    }

    options = [
        '-dSAFER',
        '-dBATCH',
        '-dNOPAUSE',
        '-sDEVICE=tiffg4',
        '-r300',
        '-sOutputFile=%(outputfilename)s',
        "-"
        ]

try:
    ghostscript = ghostscript_subprocess()
except IOError:
    logger.exception("No GhostScript installed. PDF Pal will not be able to create thumbnails.")
    ghostscript = None
_processes['ghostscript'] = ghostscript_subprocess

class tesseract_subprocess(command_subprocess):
    bin_name = 'tesseract'

    options = [
        '%(imagefilename)s',
        '%(txtfilename)s'
    ]
_processes['tesseract'] = tesseract_subprocess

class hocr_subprocess(tesseract_subprocess):
    options = [
        '%(imagefilename)s',
        '%(txtfilename)s',
        'hocr'
    ]
_processes['hocr'] = hocr_subprocess

class tesseract_version_subprocess(tesseract_subprocess):
    options = ['-v']

try:
    hocr_enabled = False
    tesseract = tesseract_subprocess()
    try:
        hocr = hocr_subprocess()
        tess_version = tesseract_version_subprocess()
        process, output = tess_version.run_command(bad_return_code=True)

        if '-' in output:
            _, version = output.strip().split('-', 1) # should be in the form of -- tesseract-3.01\n
        else:
            _, version = output.strip().split(' ', 1) # should be in the form of -- tesseract 3.00\n

        if OLD_TESSERACT_VERSION and version.startswith('3'):
            hocr_enabled = True
            _processes['tesseract'] = hocr_subprocess # if enabled use this instead and we're extract text from hocr output instead of running command twice
            logger.info("Tesseract installed. PDF Pal will index PDFs or make PDFs searchable.")
        elif version.startswith('3') and int(version[-1]) >= 1:
            hocr_enabled = True
            _processes['tesseract'] = hocr_subprocess # if enabled use this instead and we're extract text from hocr output instead of running command twice
            logger.info("Tesseract installed. PDF Pal will index PDFs or make PDFs searchable.")
        else:
            raise Exception("Bad tesseract version: must be superior of 3.01 (%s)" % version)

    except Exception:
        logger.exception("No Tesseract installed. PDF Pal will not be able to index PDFs or make PDFs searchable.")

except IOError:
    logger.exception("No Tesseract installed. PDF Pal will not be able to index PDFs or make PDFs searchable.")
    tesseract = None
    hocr = None
    hocr_enabled = False

class hocr2pdf_subprocess(command_subprocess):
    """
        hocr2pdf -i "$page" -o "$base.pdf" < "$base.html"

        input - input tiff filename
        output - output pdf filename
        hocr_file - stdin
    """
    bin_name = 'hocr2pdf'

    options = [
        '-i',
        '%(input)s',
        '-s',
        '-o',
        '%(output)s'
    ]
try:
    hocr2pdf = hocr2pdf_subprocess()
except IOError:
    logger.exception("No hocr2pdf installed. PDF Pal will not be able to make PDFs searchable.")
    hocr2pdf = None
_processes['hocr2pdf'] = hocr2pdf_subprocess

class dumpPdfMetadata_subprocess(command_subprocess):
    """
    pdftk 5percent1.pdf dump_data output info.txt

    output - filename for info file
    the input pdf comes from the stdin
    """
    bin_name = 'pdftk'
    throw_exception = True

    options = [
        '-',
        'dump_data',
        'output',
        '%(output)s'
    ]
try:
    dumpPdfMetadata = dumpPdfMetadata_subprocess()
except IOError:
    logger.exception("No pdftk installed. PDF Pal will not be able to make PDFs searchable.")
    dumpPdfMetadata = None
_processes['dumpPdfMetadata'] = dumpPdfMetadata_subprocess

class copyPdfMetadata_subprocess(command_subprocess):
    """
    pdftk z.pdf update_info info.txt output test.pdf

    info_file - filename for pdf info file
    input is stdin
    outputs to stdout
    """
    bin_name = 'pdftk'
    throw_exception = True

    options = [
        '%(input)s',
        'update_info',
        '%(info_file)s',
        'output',
        '%(output)s'
    ]
try:
    copyPdfMetadata = copyPdfMetadata_subprocess()
except IOError:
    copyPdfMetadata = None
_processes['copyPdfMetadata'] = copyPdfMetadata_subprocess

class tiff2pdf_process(command_subprocess):
    bin_name = 'tiff2pdf'
    throw_exception = True
    options = [
        '-o',
        '%(output)s',
        '%(input)s'
    ]
try:
    tiff2pdf = tiff2pdf_process()
except:
    logger.exception("tiff2pdf not installed!")
    tiff2pdf = None
_processes['tiff2pdf'] = tiff2pdf_process

class combinePDFs_subprocess(command_subprocess):
    """
    gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile="$output" "$tmpdir"/page-*.pdf

    input_files - wildcard filename to specify files to combine
    output - output filename
    """
    shell = True
    throw_exception = True
    bin_name = 'pdftk'

    options = [
        '%(input_files)s',
        'cat',
        'output',
        '%(output)s'
    ]
try:
    combinePDFs = combinePDFs_subprocess()
except IOError:
    combinePDFs = None
_processes['combinePDFs'] = combinePDFs_subprocess

class optimize_subprocess(command_subprocess):
    """
    gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile="$output" "$tmpdir"/page-*.pdf

    input_files - wildcard filename to specify files to combine
    output - output filename
    """
    shell=True
    throw_exception = True
    bin_name = 'gs'

    options = [
        '-q',
        '-dNOPAUSE',
        '-dBATCH',
        '-sDEVICE=pdfwrite',
        '-dCompatibilityLevel=1.6',
        '-dQUIET',
        '-sOutputFile=%(output)s',
        '%(input)s'
    ]
try:
    optimize = optimize_subprocess()
except IOError:
    optimize = None
_processes['optimize'] = optimize_subprocess

class pdftk_split_subprocess(command_subprocess):
    """
    pdftk filename.pdf cat 1-400 output output.pdf
    """
    throw_exception = True
    bin_name = 'pdftk'

    options = [
        '%(input)s',
        'cat',
        '%(start)d-%(end)d',
        'output',
        '%(output)s'
    ]
try:
    pdftk_split = pdftk_split_subprocess()
except IOError:
    pdftk_split = None
_processes['pdftk_split'] = pdftk_split_subprocess

class pdftk_numpage_subprocess(command_subprocess):
    """
    pdftk filename.pdf dump_data output | grep -i NumberOfPages

    pdftk_numpage.numpages(opt_values={'filename' : filename})
    """
    throw_exception = True
    bin_name = 'pdftk'

    options = [
        '%(filename)s',
        'dump_data',
        'output',
    ]
    def numpages(self, opt_values):
        try:
            process, output = self.run_command(opt_values=opt_values)
            for line in output.splitlines():
                if line.strip().startswith('NumberOfPages'):
                    return int(line.replace('NumberOfPages:', ''))
        except:
            return 0
try:
    pdftk_numpage = pdftk_numpage_subprocess()
except IOError:
    pdftk_numpage = None
_processes['pdftk_numpage'] = pdftk_numpage_subprocess

if hocr and hocr_enabled and combinePDFs and copyPdfMetadata and dumpPdfMetadata:
    hocr_enabled = True
else:
    hocr_enabled = False

def get_command(name):
    try:
        return _processes[name]()
    except:
        return None

