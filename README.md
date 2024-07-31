# OCRmyPDF Azure AI Document Intelligence

This is plugin to run OCRmyPDF with the [Azure AI Document Intelligence](https://azure.microsoft.com/en-us/products/ai-services/ai-document-intelligence) instead of Tesseract OCR,
the default OCR engine for OCRmyPDF. Hopefully it will be more performant and accurate than Tesseract OCR.

It is currently experimental and does not implement all of the features of
OCRmyPDF with Tesseract, and still relies on Tesseract for certain operations.

## Installation

To use this plugin, first install OCRmyPDF-AzureAIDocumentIntelligence to the same virtual environment:

```bash
pip install git+https://github.com/tssujt/OCRmyPDF-AzureAIDocumentIntelligence.git
```

The OCRmyPDF-AzureAIDocumentIntelligence will override Tesseract for OCR; however, OCR still depends
on Tesseract for some tasks.

## TODO

Contributions, especially pull requests are quite welcome!

At the moment this plugin is alpha status and missing some essential features:

- Tesseract is still required for determine page skew and for orientation correction
