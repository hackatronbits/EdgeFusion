from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from werkzeug.utils import secure_filename
from pdfredact import redact_pii

app = Flask(__name__)

# Folder to store uploaded and redacted files
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Home page
@app.route('/')
def home():
    return render_template("index.html")



# Handle file upload and redaction
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

        # Perform redaction
        redacted_file_path = redact_pii(filepath)
        redacted_filename = os.path.basename(redacted_file_path)

        # Redirect to download
        return redirect(url_for('download_file', filename=redacted_filename))

# Serve redacted file
@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
