import re
import fitz  # PyMuPDF

# Focused redaction patterns
patterns = [

    # Indian phone numbers (starting with 6–9, optionally with +91)
    r"\b(?:\+91[\-\s]?)?[6-9]\d{9}\b",

   
]

# Load and redact PDF
doc = fitz.open("form.pdf")

for page in doc:
    text = page.get_text()
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            matched_text = match.group().strip()
            rects = page.search_for(matched_text)
            for rect in rects:
                page.add_redact_annot(rect, fill=(0, 0, 0))  # Black out
    page.apply_redactions()

# Save final redacted PDF
doc.save("redacted_phone.pdf")
print("✅ Redacted PDF saved as 'redacted_phone.pdf'")
