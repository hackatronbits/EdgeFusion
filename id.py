import re
import fitz  # PyMuPDF

# Redaction patterns for SSN, Voter ID, PAN, Aadhaar, Passport
patterns = [
    # Aadhaar (XXXX XXXX XXXX or XXXXXXXXXXXX)
    r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",

    # PAN (ABCDE1234F)
    r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",

    # Voter ID (commonly 3 letters + 7 digits)
    r"\b[A-Z]{3}[0-9]{7}\b",

    # Passport Number (Indian: 1 letter + 7 digits or 2 letters + 7 digits)
    r"\b[A-Z]{1,2}[0-9]{7}\b",

]

# Load and redact PDF
doc = fitz.open("aadhar.pdf")

for page in doc:
    text = page.get_text()
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            matched_text = match.group().strip()
            rects = page.search_for(matched_text)
            for rect in rects:
                page.add_redact_annot(rect, fill=(0, 0, 0))  # Black fill
    page.apply_redactions()

# Save final redacted PDF
doc.save("redacted_id_info.pdf")
print("✅ Redacted PDF saved as 'redacted_id.jpg'")
