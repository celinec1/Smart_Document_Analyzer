import os
import threading
from queue import Queue
import fitz  # PyMuPDF
# import nltk
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import openai

# Initialize Flask application
app = Flask(__name__)

# Application configuration
UPLOAD_FOLDER = 'MyNewFolder'
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'jpeg'}
openai.api_key = ''

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize a task queue
task_queue = Queue()

def allowed_file(filename):
    """Check if the uploaded file type is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def summarize_text(text):
    """Use OpenAI to summarize the provided text."""
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
    """Generate a search query based on the summary using OpenAI."""
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

def process_file(file_path, filename):
    """Process uploaded files: Read, summarize, and generate a PDF summary."""
    # Determine file type and read content
    text = ""
    if filename.endswith('.txt'):
        with open(file_path, 'r') as f:
            text = f.read()
    elif filename.endswith('.pdf'):
        with fitz.open(file_path) as doc:
            text = " ".join(page.get_text() for page in doc)

    # Process text: summarize and generate search query
    paragraphs = text.split('\n\n')
    paragraph_summaries = [summarize_text(paragraph) for paragraph in paragraphs]
    overall_summary = summarize_text(text)
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
    text_object.textLine("\nSearch Query (For Internal Use):")
    text_object.textLine(search_query)
    c.drawText(text_object)
    c.save()

    # Log completion (or you could update a status in a database or file)
    print(f"Processed and summarized: {filename}")

def worker():
    """Background worker thread to process tasks from the queue."""
    while True:
        task = task_queue.get()
        if task is None:
            # Sentinel value to end the worker thread
            break
        file_path, filename = task
        process_file(file_path, filename)
        task_queue.task_done()

@app.route('/text_nlp_analysis', methods=['POST'])
def text_nlp_analysis_api():
    """API endpoint for uploading and processing text files."""
    if 'file' not in request.files:
        return jsonify({"error": "File part is missing"}), 400
    file = request.files['file']
    if not file or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Add the file processing task to the queue
    task_queue.put((file_path, filename))

    return jsonify({"status": "File upload received, processing in queue"})

if __name__ == '__main__':
    # nltk.download('punkt')
    # Start the worker thread as a daemon so it shuts down with the main process
    threading.Thread(target=worker, daemon=True).start()
    app.run
