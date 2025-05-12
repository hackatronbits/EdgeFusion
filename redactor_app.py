from flask import Flask, render_template_string, request, send_file
from pdf2image import convert_from_bytes
from fpdf import FPDF
import pytesseract
import re
import os
from werkzeug.utils import secure_filename
from nltk import download

# Ensure NLTK is ready
download('punkt')
download('averaged_perceptron_tagger')
download('maxent_ne_chunker')
download('words')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['REDACTED_FOLDER'] = 'static'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['REDACTED_FOLDER'], exist_ok=True)

# HTML template inline
INDEX_HTML = """
<!DOCTYPE html>
<html>
<head><title>PDF Redactor</title></head>
<body>
  <h2>Upload PDF and Select Redaction Types</h2>
  <form action="/" method="post" enctype="multipart/form-data">
    <label>PDF File:</label><br>
    <input type="file" name="pdf" required><br><br>

    <label>Redact:</label><br>
    <input type="checkbox" name="redaction_types" value="name">Name<br>
    <input type="checkbox" name="redaction_types" value="email">Email<br>
    <input type="checkbox" name="redaction_types" value="phone">Phone<br>
    <input type="checkbox" name="redaction_types" value="aadhaar">Aadhaar<br><br>

    <input type="submit" value="Redact PDF">
  </form>
</body>
</html>
"""

def extract_text_from_pdf(file_bytes):
    images = convert_from_bytes(file_bytes)
    return [pytesseract.image_to_string(img) for img in images]

def redact_text(text_by_page, types):
    redacted_pages = []

    for text in text_by_page:
        if 'email' in types:
            text = re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', '[REDACTED EMAIL]', text)
        if 'phone' in types:
            text = re.sub(r'\b\d{10}\b', '[REDACTED PHONE]', text)
        if 'aadhaar' in types:
            text = re.sub(r'\b\d{4}\s\d{4}\s\d{4}\b', '[REDACTED AADHAAR]', text)
        if 'name' in types:
            text = re.sub(r'\b[A-Z][a-z]+\s[A-Z][a-z]+\b', '[REDACTED NAME]', text)
        redacted_pages.append(text)

    return redacted_pages

def save_redacted_pdf(pages, filename):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    for text in pages:
        pdf.add_page()
        pdf.multi_cell(0, 10, text)

    output_path = os.path.join(app.config['REDACTED_FOLDER'], filename)
    pdf.output(output_path)
    return output_path

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        pdf = request.files['pdf']
        redaction_types = request.form.getlist('redaction_types')

        filename = secure_filename(pdf.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        pdf.save(filepath)

        with open(filepath, 'rb') as f:
            raw_bytes = f.read()

        extracted = extract_text_from_pdf(raw_bytes)
        redacted = redact_text(extracted, redaction_types)
        redacted_file = save_redacted_pdf(redacted, f"redacted_{filename}.pdf")

        return send_file(redacted_file, as_attachment=True)

    return render_template_string(INDEX_HTML)

if __name__ == "__main__":
    app.run(debug=True)
