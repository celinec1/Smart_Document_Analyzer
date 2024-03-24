import os
import fitz  # PyMuPDF
import nltk
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import openai

app = Flask(__name__)

# the upload_folder is a placeholder for now
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'jpeg'}
openai.api_key = 'my_openai_key'

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

def generate_search_query(summary):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Generate a concise search query based on this summary:\n\n{summary}",
        temperature=0.5,
        max_tokens=60,
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

    # Read and summarize file content
    text = ""
    if filename.endswith('.txt'):
        with open(file_path, 'r') as f:
            text = f.read()
    elif filename.endswith('.pdf'):
        with fitz.open(file_path) as doc:
            text = " ".join(page.get_text() for page in doc)

    paragraphs = text.split('\n\n')
    paragraph_summaries = [summarize_text(paragraph) for paragraph in paragraphs]
    overall_summary = summarize_text(text)

    # this search query is for the feed ingester
    search_query = generate_search_query(overall_summary)

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
    # have to test to see if google search works
    text_object.textLine("\nSearch Query (For Internal Use):")
    text_object.textLine(search_query)
    c.drawText(text_object)
    c.save()

    # Save the search query for use in feed ingester api
    with open(os.path.join(app.config['UPLOAD_FOLDER'], f"{filename}_search_query.txt"), "w") as f:
        f.write(search_query)

    return jsonify({"status": "Analysis complete", "summary_pdf": summary_pdf_path, "search_query": search_query})

if __name__ == '__main__':
    nltk.download('punkt')
    app.run(debug=True)
