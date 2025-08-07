import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import pytesseract
import fitz  # PyMuPDF
from PIL import Image

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
        doc = fitz.open(filepath)
        all_text = ""
        max_pages = 10  # optional safety for free hosting

        for page_num in range(min(len(doc), max_pages)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=300)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"page_{page_num}.png")
            pix.save(image_path)

            with Image.open(image_path) as image:
                image = image.convert("RGB")  # Ensure compatibility with Tesseract
                text = pytesseract.image_to_string(image)
                all_text += f"\n\n--- Page {page_num + 1} ---\n{text.strip()}"

            os.remove(image_path)

        return jsonify({"extracted_text": all_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
