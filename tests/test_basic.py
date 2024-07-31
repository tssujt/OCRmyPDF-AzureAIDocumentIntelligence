# SPDX-FileCopyrightText: 2023 James R. Barlow
# SPDX-License-Identifier: MIT

import ocrmypdf
import ocrmypdf_azureaidocumentintelligence  # noqa: F401
import pytest


def test_azureaidocumentintelligence(resources, outpdf):
    with pytest.raises(ValueError):
        ocrmypdf.ocr(resources / "jbig2.pdf", outpdf, pdf_renderer="sandwich")
