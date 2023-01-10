"""Wrapper for OCR module."""
import sys
import os

import fitz


LANG = 'ukr+eng'
DPI = 300


def get_pages(stream):
    """Read document pages from data bytes."""
    return [
        page.get_textpage_ocr(language=LANG, dpi=DPI).extractText()
        for page in fitz.open(stream=stream)]


if __name__ == '__main__':
    print(os.environ['TESSDATA_PREFIX'])
    preview = get_pages(open(sys.argv[1], 'rb').read())
    print(preview)
