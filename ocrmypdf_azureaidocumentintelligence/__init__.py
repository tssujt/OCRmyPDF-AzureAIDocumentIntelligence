# SPDX-FileCopyrightText: 2023 James R. Barlow
# SPDX-License-Identifier: MIT

"""Azure AI Document Intelligence plugin for OCRmyPDF."""

from __future__ import annotations

import logging
import os
import time
from typing import Optional

import cv2 as cv
import pluggy
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult
from azure.core.credentials import AzureKeyCredential
from ocrmypdf import OcrEngine, hookimpl
from ocrmypdf._exec import tesseract

from ocrmypdf_azureaidocumentintelligence._cv import detect_skew
from ocrmypdf_azureaidocumentintelligence._azureaidocumentintelligence import (
    extract_words,
)
from ocrmypdf_azureaidocumentintelligence._pdf import (
    azure_ai_document_intelligence_to_pikepdf,
)

log = logging.getLogger(__name__)


@hookimpl
def initialize(plugin_manager: pluggy.PluginManager):
    pass


@hookimpl
def add_options(parser):
    azureaidocumentintelligence_options = parser.add_argument_group(
        "Azure AI Document Intelligence", "Azure AI Document Intelligence options"
    )
    azureaidocumentintelligence_options.add_argument(
        "--azure-ai-document-intelligence-endpoint", type=str
    )
    azureaidocumentintelligence_options.add_argument(
        "--azure-ai-document-intelligence-api-key", type=str
    )
    azureaidocumentintelligence_options.add_argument(
        "--azure-ai-document-intelligence-debug-suppress-images",
        action="store_true",
        dest="azure_ai_document_intelligence_debug_suppress_images",
    )


@staticmethod
def call_azure_service(
    endpoint: str,
    api_key: str,
    input_file: str,
    attempts: int = 5,
    initial_delay: int = 1,
) -> Optional[AnalyzeResult]:
    """
    Calls the Azure AI Document Intelligence with exponential backoff.
    """
    if not endpoint or not api_key:
        raise ValueError("Azure AI Document Intelligence credentials not found")

    credential = AzureKeyCredential(api_key)
    document_intelligence_client = DocumentIntelligenceClient(endpoint, credential)
    for attempt in range(attempts):
        try:
            with open(input_file, "rb") as f:
                poller = document_intelligence_client.begin_analyze_document(
                    "prebuilt-read",
                    analyze_request=f,
                    content_type="application/octet-stream",
                )
                reader: AnalyzeResult = poller.result()
            return reader
        except Exception as e:
            log.warning(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(initial_delay * (2**attempt))  # Exponential backoff

    log.error(
        "All attempts to call the Azure AI Document Intelligence service have failed."
    )
    return None


class AzureAIDocumentIntelligenceEngine(OcrEngine):
    """Implements OCR with Azure AI Document Intelligence."""

    @staticmethod
    def version():
        return "0.1.0"

    @staticmethod
    def creator_tag(options):
        tag = "-PDF" if options.pdf_renderer == "sandwich" else ""
        return f"AzureAIDocumentIntelligence{tag} {AzureAIDocumentIntelligenceEngine.version()}"

    def __str__(self):
        return f"AzureAIDocumentIntelligence {self.version()}"

    @staticmethod
    def languages(options):
        return tesseract.get_languages()

    @staticmethod
    def get_orientation(input_file, options):
        return tesseract.get_orientation(
            input_file,
            engine_mode=options.tesseract_oem,
            timeout=options.tesseract_non_ocr_timeout,
        )

    @staticmethod
    def get_deskew(input_file, options) -> float:
        img = cv.imread(os.fspath(input_file))
        angle = detect_skew(img)
        log.debug(f"Detected skew angle: {angle:.2f} degrees")
        return angle

    @staticmethod
    def generate_hocr(input_file, output_hocr, output_text, options):
        raise NotImplementedError(
            "AzureAIDocumentIntelligenceEngine does not support hOCR output"
        )

    @staticmethod
    def generate_pdf(input_file, output_pdf, output_text, options):
        results = []

        # Read the file
        reader = call_azure_service(
            options.azure_ai_document_intelligence_endpoint,
            options.azure_ai_document_intelligence_api_key,
            input_file,
        )
        if reader is not None:
            results = extract_words(reader)
        else:
            # Handle the failure case
            pass

        text = " ".join([result.text for result in results])
        output_text.write_text(text)

        azure_ai_document_intelligence_to_pikepdf(
            input_file,
            1.0,
            results,
            output_pdf,
            boxes=options.azure_ai_document_intelligence_debug_suppress_images,
        )


@hookimpl
def get_ocr_engine():
    return AzureAIDocumentIntelligenceEngine()
