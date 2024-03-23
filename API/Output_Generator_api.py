from flask import Flask, request, jsonify, send_file
import fitz  
import os

app = Flask(__name__)

# as a placeholder
UPLOAD_FOLDER = 'uploads'

@app.route('/get_analysis_output', methods=['GET'])
def get_analysis_output():
    # Retrieve the original filename from the query parameter
    original_filename = request.args.get('filename')

    if not original_filename:
        return jsonify({"error": "Filename is required"}), 400

    # Construct the analysis PDF filename
    # have to change name, it is a placeholder for now
    analysis_pdf_filename = f"NLP_analysis_{original_filename}.pdf"
    analysis_pdf_path = os.path.join(UPLOAD_FOLDER, analysis_pdf_filename)

    # Ensure the analysis PDF file exists
    if not os.path.exists(analysis_pdf_path):
        return jsonify({"error": "Analysis file not found"}), 404

    # Open and read the PDF file
    try:
        doc = fitz.open(analysis_pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return jsonify({"content": text})
    except Exception as e:
        return jsonify({"error": "Failed to read analysis", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
