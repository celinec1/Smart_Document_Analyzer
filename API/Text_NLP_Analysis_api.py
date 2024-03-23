from flask import Flask, request, jsonify
import fitz  
import nltk
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import openai

# Using openai to do the NLP analysis. It will put a pdf of the analysis made
openai.api_key = 'my_api_key'

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads' # have to change to the folder that is being uploaded via secure_file_uploader
ALLOWED_EXTENSIONS = {'pdf', 'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def summarize_text(text):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Summarize this text:\n\n{text}",
        temperature=0.7,
        max_tokens=150,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    return response.choices[0].text.strip()

@app.route('/text_nlp_analysis', methods=['POST'])
def text_nlp_analysis_api():
    if 'file' not in request.files:
        return jsonify({"error": "File part is missing"}), 400
    file = request.files['file']
    if not file or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Read file content
    text = ""
    if filename.endswith('.txt'):
        with open(file_path, 'r') as f:
            text = f.read()
    elif filename.endswith('.pdf'):
        with fitz.open(file_path) as doc:
            text = " ".join(page.get_text() for page in doc)

    # Process for summarization
    paragraphs = text.split('\n\n')
    paragraph_summaries = [summarize_text(paragraph) for paragraph in paragraphs]
    overall_summary = summarize_text(text)

    # Generate PDF with summaries
    summary_pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], f"NLP_analysis_{filename}.pdf")
    c = canvas.Canvas(summary_pdf_path, pagesize=letter)
    text_object = c.beginText(40, 750)
    text_object.textLine("Overall Summary:")
    text_object.textLine(overall_summary)
    text_object.textLine("\nParagraph Summaries:")
    for summary in paragraph_summaries:
        text_object.textLine(summary)
        text_object.textLine("")
    c.drawText(text_object)
    c.save()

    return jsonify({"status": "Analysis complete", "summary_pdf": summary_pdf_path})

if __name__ == '__main__':
    nltk.download('punkt')
    app.run(debug=True)
