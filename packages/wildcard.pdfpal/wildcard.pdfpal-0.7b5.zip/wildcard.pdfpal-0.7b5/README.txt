Introduction
============
This package provides some nice integrations for PDF heavy web sites.

* Generates thumbnails from PDF
* Adds folder view for pdfs so it can use the generated thumbnail
* Adds OCR for PDF indexing
* Everything configurable so you can choose to not use thumbnail gen or OCR
* Ability to create searchable PDFs with HOCR
* use the `@@async-monitor` url to monitor asynchronous jobs that have yet to run


OCR
---

OCR requires Ghostscript to be installed and Tesseract. Just you package management
to install these packages:

  # sudo apt-get install ghostscript tesseract-ocr

This will install tessact 2 not tesseract 3.

Searchable PDFs
---------------

Requires svn checkout of tesseract version 3.01 or 3.00 with the hocr configuration in place.
Take a look at this thread to find out how to configure hocr http://ubuntuforums.org/showthread.php?t=1647350

In addition, you'll need exactimage and pdftk installed

  # sudo apt-get install exactimage pdftk libtiff-tools

To not use the latest tesseract version to will have to add this in your
instances declaration:

  environment-vars += AUTHORIZE_OLD_TESSERACT_VERSION true


Plone 3
-------

* Requires hashlib


Extra
-----

You can convert all at once by calling the url `@@queue-up-all`.

