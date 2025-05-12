# gem.py
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from werkzeug.utils import secure_filename
from pdfredact import redact_pii
from functions import redact_email, redact_name, redact_phone, redact_aadhaar, redact_pan, redact_passport, redact_voter_id, redact_bank_account
import fitz  # PyMuPDF

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads/'
REDACTED_FOLDER = 'redacted_pdfs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REDACTED_FOLDER'] = REDACTED_FOLDER
# ensuring the upload and redacted folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REDACTED_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template("index.html")



@app.route('/upload_file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        redaction_type = request.form.get('dataType')
        custom_types = request.form.getlist('custom_types')
        # doing redaction based on selected type
        if redaction_type == "default":
            redacted_file = redact_pii(filepath)
        elif redaction_type == "custom":
            # Redact only the selected custom types
            redacted_file = redact_custom(filepath, custom_types)
            # Save the redacted file
        redacted_filename = os.path.basename(redacted_file)
        return redirect(url_for('download_file', filename=redacted_filename))

@app.route('/uploads/<filename>')
def download_file(filename):
    return f"File redacted and saved as: {filename}"
    



def redact_custom(filepath, custom_types):
    """
    Redacts specific types of PII based on user selection from a PDF file.
    :param filepath: Path to the input PDF file
    :param custom_types: List of selected PII types to redact
    :return: Path to the redacted PDF file
    """
    # Open the PDF file
    doc = fitz.open(filepath)

    for page in doc:
        text = page.get_text()
        
        # Apply redaction functions based on selected types
        if "email" in custom_types:
            text = redact_email(text)
        if "name" in custom_types:
            text = redact_name(text)
        if "phone" in custom_types:
            text = redact_phone(text)
        if "address" in custom_types:
            text = redact_aadhaar(text)
        if "ssn" in custom_types:
            text = redact_pan(text)
        if "govtid" in custom_types:
            text = redact_passport(text)
        if "financial" in custom_types:
            text = redact_bank_account(text)

        # Clear the page and insert redacted text
        page.clean_contents()
        page.insert_text((72, 72), text, fontsize=12)

    redacted_filepath = os.path.join(app.config['REDACTED_FOLDER'], f"redacted_{os.path.basename(filepath)}")
    doc.save(redacted_filepath)
    doc.close()

    return redacted_filepath



if __name__ == "__main__":
    app.run(debug=True, port=5000)