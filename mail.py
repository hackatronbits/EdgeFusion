import re
import fitz  # PyMuPDF

# Focused redaction patterns
patterns = [
    # Email address
    r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}\b",

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
doc.save("redacted_email.pdf")
print("✅ Redacted PDF saved as 'redacted_email.pdf'")
