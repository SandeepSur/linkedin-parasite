import os
import tempfile
import traceback
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import pytesseract
import fitz  # PyMuPDF
from PIL import Image

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Save the file temporarily
        filename = secure_filename(file.filename)
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        file.save(temp_pdf.name)

        doc = fitz.open(temp_pdf.name)
        all_text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=300)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_img:
                pix.save(temp_img.name)
                image = Image.open(temp_img.name)
                text = pytesseract.image_to_string(image)
                all_text += f"\n\n--- Page {page_num + 1} ---\n{text.strip()}"
                image.close()
                os.remove(temp_img.name)

        os.remove(temp_pdf.name)
        return jsonify({"extracted_text": all_text})

    except Exception as e:
        error_trace = traceback.format_exc()
        print("=== TRACEBACK ===")
        print(error_trace)
        return jsonify({
            "error": str(e),
            "trace": error_trace
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
