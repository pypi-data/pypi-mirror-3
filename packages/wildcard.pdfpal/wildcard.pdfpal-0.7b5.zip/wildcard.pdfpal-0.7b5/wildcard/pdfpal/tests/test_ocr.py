import unittest2 as unittest
from plone.app.testing import login
from base import PalTestCase, FakeSubProcess
from DateTime import DateTime

_hocr_test_data = """
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<title></title>
<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
<meta name='ocr-system' content='tesseract'/>
</head>
<body>
<div class='ocr_page' id='page_1' title='image "image_0001.tiff"; bbox 0 0 2118 2740'>
<div class='ocr_carea' id='block_1_1' title="bbox 371 800 1809 856">
<p class='ocr_par'>
<span class='ocr_line' id='line_1_1' title="bbox 371 800 1809 856"><span class='ocr_word' id='word_1_1' title="bbox 371 800 724 853"><span class='xocr_word' id='xword_1_1' title="x_wconf -4">some</span></span>
<span class='ocr_word' id='word_1_2' title="bbox 749 801 1069 855"><span class='xocr_word' id='xword_1_2' title="x_wconf -3">text</span></span>
<span class='ocr_word' id='word_1_3' title="bbox 1091 800 1186 855"><span class='xocr_word' id='xword_1_3' title="x_wconf -3">that</span></span>
<span class='ocr_word' id='word_1_5' title="bbox 1210 801 1809 857"><span class='xocr_word' id='xword_1_4' title="x_wconf -5">is</span></span>
<span class='ocr_word' id='word_1_6' title="bbox 1210 801 1809 858"><span class='xocr_word' id='xword_1_5' title="x_wconf -5">in</span></span>
<span class='ocr_word' id='word_1_7' title="bbox 1210 801 1809 859"><span class='xocr_word' id='xword_1_6' title="x_wconf -5">the</span></span>
<span class='ocr_word' id='word_1_8' title="bbox 1210 801 1809 860"><span class='xocr_word' id='xword_1_7' title="x_wconf -5">pdf</span></span>
</p>
</div>
</div>
<div class='ocr_page' id='page_2' title='image "image_0002.tiff"; bbox 2 0 2118 2740'>
<div class='ocr_carea' id='block_2_1' title="bbox 372 800 1809 856">
<p class='ocr_par'>
<span class='ocr_line' id='line_2_1' title="bbox 371 800 1809 956"><span class='ocr_word' id='word_2_1' title="bbox 471 800 724 853"><span class='xocr_word' id='xword_2_1' title="x_wconf -4">page</span></span>
<span class='ocr_word' id='word_2_2' title="bbox 749 801 1069 957"><span class='xocr_word' id='xword_2_2' title="x_wconf -3">2</span></span>
<span class='ocr_word' id='word_2_3' title="bbox 1091 800 1186 958"><span class='xocr_word' id='xword_2_3' title="x_wconf -3">of</span></span>
<span class='ocr_word' id='word_2_4' title="bbox 1210 801 1809 959"><span class='xocr_word' id='xword_2_4' title="x_wconf -5">the</span></span>
<span class='ocr_word' id='word_2_5' title="bbox 1210 801 1809 960"><span class='xocr_word' id='xword_2_4' title="x_wconf -5">pdf</span></span>
</p>
</div>
</div>
</body>
</html>
"""

class TestOCR(PalTestCase):

    def setUp(self):
        from wildcard.pdfpal import ocr
        ocr.hocr_enabled = True

        self.combinePDFs = FakeSubProcess()
        self._combinePDFs_orig = ocr.combinePDFs
        ocr.combinePDFs = self.combinePDFs

        self.hocr2pdf = FakeSubProcess()
        self._hocr2pdf_orig = ocr.hocr2pdf
        ocr.hocr2pdf = self.hocr2pdf

        def tess_run_command(opt_values=None, stdin=None):
            fi = open(opt_values['txtfilename'] + '.html', 'w')
            fi.write(_hocr_test_data)
            fi.close()
            return None, None
        self.tesseract = FakeSubProcess(run_command=tess_run_command)
        self._tesseract_orig = ocr.tesseract
        ocr.tesseract = self.tesseract

        self.dumpPdfMetadata = FakeSubProcess()
        self._dumpPdfMetadata_orig = ocr.dumpPdfMetadata
        ocr.dumpPdfMetadata = self.dumpPdfMetadata

        self.copyPdfMetadata = FakeSubProcess()
        self._copyPdfMetadata_orig = ocr.copyPdfMetadata
        ocr.copyPdfMetadata = self.copyPdfMetadata

    def tearDown(self):
        from wildcard.pdfpal import ocr
        ocr.combinePDFs = self._combinePDFs_orig
        ocr.hocr2pdf = self._hocr2pdf_orig
        ocr.tesseract = self._tesseract_orig
        ocr.copyPdfMetadata = self._copyPdfMetadata_orig
        ocr.dumpPdfMetadata = self._dumpPdfMetadata_orig

    def test_ocr_sets_file_hash(self):
        from wildcard.pdfpal.ocr import index_pdf

        login(self.layer['portal'], 'admin')
        pdf = self.createPDF(id="someid")
        index_pdf(pdf)

        from wildcard.pdfpal.settings import PDFSettings
        settings = PDFSettings(pdf)
        self.failUnless(settings.file_hash is not None)


    def test_ocr_sets_when_last_done(self):
        from wildcard.pdfpal.ocr import index_pdf

        login(self.layer['portal'], 'admin')
        pdf = self.createPDF(id="someid")
        index_pdf(pdf)

        from wildcard.pdfpal.settings import PDFSettings
        settings = PDFSettings(pdf)

        self.failUnless(DateTime(settings.ocr_last_updated) > DateTime('1999/01/01'))

    def test_should_not_ocr_if_file_has_not_changed(self):
        from wildcard.pdfpal.ocr import index_pdf

        login(self.layer['portal'], 'admin')
        pdf = self.createPDF(id="someid")

        from wildcard.pdfpal.settings import PDFSettings
        settings = PDFSettings(pdf)
        ndate = DateTime().ISO8601()
        settings.ocr_last_updated = ndate

        index_pdf(pdf)

        self.failUnless(settings.ocr_last_updated == ndate)

    def test_should_ocr_if_mod_date_has_changed(self):
        from wildcard.pdfpal.ocr import index_pdf
        from wildcard.pdfpal.settings import PDFSettings

        login(self.layer['portal'], 'admin')
        pdf = self.createPDF(id="someid")
        settings = PDFSettings(pdf)

        date = DateTime('1999/01/01').ISO8601()
        settings.ocr_last_updated = date

        index_pdf(pdf)

        self.failUnless(settings.ocr_last_updated != date)


    def test_only_ocr_if_file_hash_different(self):
        from wildcard.pdfpal.ocr import index_pdf

        login(self.layer['portal'], 'admin')
        pdf = self.createPDF(id="someid")

        from wildcard.pdfpal.settings import PDFSettings
        settings = PDFSettings(pdf)
        settings.file_hash = 'foobar'
        index_pdf(pdf)

        self.failUnless(settings.file_hash != 'foobar')

    def test_do_not_ocr_if_file_hash_the_same(self):
        from wildcard.pdfpal.ocr import index_pdf, get_hash

        login(self.layer['portal'], 'admin')
        pdf = self.createPDF(id="someid")

        from wildcard.pdfpal.settings import PDFSettings
        settings = PDFSettings(pdf)
        settings.file_hash = get_hash(str(pdf.getFile().data))
        index_pdf(pdf)

        self.failUnless(DateTime(settings.ocr_last_updated) < DateTime('1999/01/01'))

    def test_hocr_is_run(self):
        from wildcard.pdfpal import ocr

        login(self.layer['portal'], 'admin')
        pdf = self.createPDF(id="someid")
        ocr.index_pdf(pdf)

        field = pdf.getField('ocrText')
        self.failUnless('some text that is in the pdf' in field.get(pdf))
        self.failUnless('page 2 of the pdf' in field.get(pdf))

    def test_tesseract_run_for_each_page_in_pdf(self):
        from wildcard.pdfpal import ocr

        login(self.layer['portal'], 'admin')
        pdf = self.createPDF(id="someid")

        ocr.index_pdf(pdf)
        self.assertEquals(len(self.tesseract.runs), 2)

    def test_manual_trigger_of_pdf_works(self):
        from wildcard.pdfpal.browser.views import ManualTrigger
        portal = self.layer['portal']
        login(portal, 'admin')
        pdf = self.createPDF(id="someid")

        manual = portal.restrictedTraverse('someid/@@force-indexing')
        self.assertEquals(len(self.tesseract.runs), 2)

def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestOCR))
    return suite