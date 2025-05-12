# gem.py
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session, flash
import os
from werkzeug.utils import secure_filename
from redaction import redact_pii
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = os.urandom(24)  # ✅ Added secret key for session and flash messages

# MongoDB setup for user auth
client = MongoClient('mongodb://localhost:27017/')
db = client['secure_pii']
users = db['users']

# upload directory setup
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ✅ Login system routes from log.py:

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users.find_one({'email': email})
        if user and check_password_hash(user['password'], password):
            session['user'] = user['username']
            flash(f"Welcome back, {user['username']}!", "success")
            return redirect(url_for('home'))  # ✅ Redirect to home
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        if users.find_one({'email': email}):
            return render_template('signup.html', error="Email already exists")

        users.insert_one({'username': username, 'email': email, 'password': password})
        flash("Account created successfully! Please log in.", "success")
        return redirect('/login')
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("You have been logged out.", "info")
    return redirect('/login')

@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template("index.html", username=session['user'])  # ✅ send username to template

    

# file upload and redaction route
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

        # redacted_file_path = redact_pii(filepath)


        # Get user redaction choice
        redaction_type = request.form.get('dataType')
        custom_types = request.form.getlist('custom_types') if redaction_type == "custom" else []

        # Pass selection to redaction function
        redacted_file_path = redact_pii(filepath, redaction_type=redaction_type, custom_types=custom_types)
        redacted_filename = os.path.basename(redacted_file_path)
        return redirect(url_for('download_file', filename=redacted_filename))

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, port=5000)