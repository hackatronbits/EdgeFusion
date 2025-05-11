from flask import Flask, url_for, render_template, request, redirect
import os #using this module to save pdf file in our system ig
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Folder to store uploaded files
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Make sure the folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/')
def home():
    return render_template("index.html")



@app.route("/downloads")
def downloads():
    return render_template("downloads.html")  # Or any logic you want



@app.route('/uploads', methods=["GET", "POST"])
def uploads():
    if request.method == "POST":
        pdf_file = request.files.get("file")
        
        if pdf_file and pdf_file.filename !="":
            filename = secure_filename(pdf_file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            pdf_file.save(save_path)
            # return redirect(url_for("upload"))

            return f"File saved at: {save_path}"  # Or redirect to another page
        
        
        return "No file uploaded", 400
    
        
    else:
        return render_template("upload.html")
        # return "upload file hona tha but now just testing"
   
    

    








if __name__ == "__main__":
    app.run(debug=True)