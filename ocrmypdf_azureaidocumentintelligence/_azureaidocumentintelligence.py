# SPDX-FileCopyrightText: 2023 James R. Barlow
# SPDX-License-Identifier: MIT

"""Interface to Azure AI Document Intelligence."""

from __future__ import annotations

from typing import List, NamedTuple

from azure.ai.documentintelligence.models import AnalyzeResult


class AzureOCRResult(NamedTuple):
    """Result of OCR with Azure AI Document Intelligence."""

    quad: list
    text: str
    confidence: float


def extract_words(reader: AnalyzeResult) -> List[AzureOCRResult]:
    # Extract word details from the first page
    word_details = []
    if reader.pages and len(reader.pages) > 0:
        first_page = reader.pages[0]
        for word in first_page.words:
            word_details.append(AzureOCRResult(word.polygon, word.content, word.confidence))

    return word_details
