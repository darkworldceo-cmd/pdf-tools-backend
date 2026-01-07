from flask import Flask, request, jsonify
import pikepdf
import tempfile
import os

app = Flask(__name__)

@app.route("/verify-signature", methods=["POST"])
def verify_signature():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        file.save(tmp.name)
        pdf_path = tmp.name

    try:
        with pikepdf.open(pdf_path) as pdf:
            sigs = []
            for page in pdf.pages:
                if "/Annots" in page:
                    for annot in page.Annots:
                        if annot.get("/Subtype") == "/Widget" and annot.get("/FT") == "/Sig":
                            sigs.append("Signature Found")

            if sigs:
                result = "Signature Found (Validation depends on certificate trust)"
            else:
                result = "No Digital Signature Found"

    except Exception as e:
        os.remove(pdf_path)
        return jsonify({"error": str(e)}), 500

    os.remove(pdf_path)

    return jsonify({
        "status": result
    })

if __name__ == "__main__":
    app.run()
