import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
import pytesseract

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in request"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        images = convert_from_path(filepath, dpi=300)
        all_text = ""
        for i, image in enumerate(images):
            text = pytesseract.image_to_string(image)
            all_text += f"\n\n--- Page {i+1} ---\n{text.strip()}"
        
        return jsonify({"extracted_text": all_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
if __name__ == '__main__':
    app.run()
