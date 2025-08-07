# app.py  – copy/paste the whole file
import os, tempfile, traceback
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import fitz                      # PyMuPDF
import pytesseract               # Tesseract wrapper

app = Flask(__name__)

@app.get("/")
def health():
    return "OK", 200             # silences Render's health-check 404s

@app.post("/upload")
def upload_file():
    if "file" not in request.files:
        return jsonify(error="No file part"), 400

    f = request.files["file"]
    if f.filename == "":
        return jsonify(error="No file selected"), 400

    try:
        # 1️⃣ save PDF to a true temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as pdf_tmp:
            f.save(pdf_tmp.name)

        doc = fitz.open(pdf_tmp.name)
        extracted = []

        for p in doc:
            # 2️⃣ render each page to a temp PNG
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as img_tmp:
                p.get_pixmap(dpi=300).save(img_tmp.name)
                # 3️⃣ hand **file path** to Tesseract
                text = pytesseract.image_to_string(img_tmp.name, lang="eng")
            os.unlink(img_tmp.name)
            extracted.append(f"--- Page {p.number+1} ---\n{text.strip()}")

        os.unlink(pdf_tmp.name)
        return jsonify(extracted_text="\n\n".join(extracted))

    except Exception as e:
        trace = traceback.format_exc()
        print(trace)
        return jsonify(error=str(e), trace=trace), 500

if __name__ == "__main__":
    app.run(debug=True)
