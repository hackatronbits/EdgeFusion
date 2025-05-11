import os
import re
import spacy
import pytesseract
from flask import Flask, render_template, request, send_file, redirect, url_for
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from fpdf import FPDF
from pdf2image import convert_from_path
from PIL import Image, ImageDraw

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

nlp = spacy.load("en_core_web_sm")

regex_patterns = {
    "email": r"\b[\w.-]+?@\w+?\.\w+?\b",
    "phone": r"(\+?\d{1,3}[-.\s]?)?\(?\d{3,5}\)?[-.\s]?\d{3,5}[-.\s]?\d{4}",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "ip": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "aadhar": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
    "pan": r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
    "voter": r"\b[A-Z]{3}[0-9]{7}\b",
    "credit_card": r"\b(?:\d[ -]*?){13,16}\b",
    "transaction_id": r"\b[a-zA-Z0-9]{10,}\b",
    "location": r"\b\d{1,3}\.\d{1,6},\s?\d{1,3}\.\d{1,6}\b"
}

def redact_text(text):
    redacted = text
    doc = nlp(text)

    for ent in doc.ents:
        if ent.label_ in ['PERSON', 'GPE', 'LOC', 'ORG']:
            redacted = redacted.replace(ent.text, '[REDACTED]')
    
    for label, pattern in regex_patterns.items():
        redacted = re.sub(pattern, '[REDACTED]', redacted, flags=re.IGNORECASE)

    return redacted

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/uploads', methods=['POST'])
def handle_upload():
    file = request.files.get('file')
    if not file or not file.filename.endswith('.pdf'):
        return "Only PDF files allowed", 400

    filename = secure_filename(file.filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(path)

    images = convert_from_path(path)
    redacted_pdf = FPDF()

    for i, img in enumerate(images):
        text = pytesseract.image_to_string(img)
        redacted_text = redact_text(text)

        blank = Image.new('RGB', img.size, color='white')
        draw = ImageDraw.Draw(blank)
        draw.text((40, 40), redacted_text[:10000], fill='black')  # Limit text length for demo

        temp_image_path = f'redacted_page_{i}.jpg'
        blank.save(temp_image_path)

        redacted_pdf.add_page()
        redacted_pdf.image(temp_image_path, x=0, y=0, w=210)
        os.remove(temp_image_path)

    output_path = os.path.join(app.config['UPLOAD_FOLDER'], f"redacted_{filename}")
    redacted_pdf.output(output_path)

    return send_file(output_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
