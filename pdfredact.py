import re
import fitz  # PyMuPDF

# General redaction patterns
patterns = [
    # Email address
    r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}\b",

    # Indian phone numbers (starting with 6–9, optionally with +91)
    r"\b(?:\+91[\-\s]?)?[6-9]\d{9}\b",

    # IFSC codes (Indian bank format)
    r"\b[A-Z]{4}0[A-Z0-9]{6}\b",

    # Credit/debit card numbers (13–19 digits, with optional space/dash)
    r"\b(?:\d[ -]?){13,19}\b",

    # UPI IDs (username@bank format)
    r"\b[a-zA-Z0-9._-]{2,256}@[a-zA-Z]{2,64}\b",

    # Aadhaar number (XXXX XXXX XXXX format)
    r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",

    # PAN number (ABCDE1234F format)
    r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",

    # US SSN (XXX-XX-XXXX format)
    r"\b\d{3}-\d{2}-\d{4}\b",

    # Dates (DD/MM/YYYY or similar)
    r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",

    # Indian PIN codes
    r"\b\d{6}\b",

    # Bank account numbers (9–18 digit numbers)
    r"\b\d{9,18}\b",

    # Transaction IDs / UTRs (12+ alphanumeric)
    r"\b[A-Z0-9]{12,}\b"
]


# # Example redaction logic
# doc = fitz.open("form.pdf")
# for page in doc:
#     text = page.get_text()
#     for pattern in patterns:
#         for match in re.finditer(pattern, text):
#             for rect in page.search_for(match.group()):
#                 page.add_redact_annot(rect, fill=(0, 0, 0))  # Black out
#     page.apply_redactions()

# doc.save("finnall_redacted.pdf")


def redact_pii(filepath):
    """
    Redacts PII from the given PDF file and saves the redacted file.
    :param filepath: Path to the input PDF file
    :return: Path to the redacted PDF file
    """
    doc = fitz.open(filepath)
    for page in doc:
        text = page.get_text()
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                for rect in page.search_for(match.group()):
                    page.add_redact_annot(rect, fill=(0, 0, 0))  # Black out
        page.apply_redactions()
    redacted_filepath = filepath.replace(".pdf", "_redacted.pdf")
    doc.save(redacted_filepath)
    return redacted_filepath