from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
import os
from werkzeug.utils import secure_filename
from pdfredact import redact_pii  # Your redaction function
from gemini_handler import get_gemini_response  # Your Gemini API handler

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload_file", methods=["POST"])
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

        redacted_file_path = redact_pii(filepath)
        redacted_filename = os.path.basename(redacted_file_path)
        return redirect(url_for('download_file', filename=redacted_filename))

@app.route("/uploads/<filename>")
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route("/gemini", methods=["POST"])
def gemini():
    data = request.get_json()
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "No input text provided"}), 400
    response = get_gemini_response(text)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True, port=8000)
