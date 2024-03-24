import requests
from PyPDF2 import PdfFileReader, PdfFileWriter
import io
from flask import Flask, request, jsonify

app = Flask(__name__)

GOOGLE_API_KEY = 'my_api_key'
GOOGLE_CSE_ID = 'my_cse_id'

def google_search(query):
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': GOOGLE_API_KEY,
        'cx': GOOGLE_CSE_ID,
        'q': query,
    }
    response = requests.get(search_url, params=params)
    result = response.json()
    
    formatted_results = []
    for item in result.get("items", []):
        title = item.get("title")
        link = item.get("link")
        formatted_results.append(f"{title}\n{link}\n")
    
    return formatted_results


@app.route('/enhance_pdf_with_search', methods=['POST'])
def enhance_pdf_with_search():
    original_filename = request.form['filename']
    search_query = request.form['search_query']

    # Perform web search
    search_results = google_search(search_query)

    # Generate a new PDF with search results
    search_results_pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], f"search_results_{original_filename}.pdf")
    c = canvas.Canvas(search_results_pdf_path, pagesize=letter)
    text_object = c.beginText(40, 750)
    text_object.textLine(f"Web Search Results for: {search_query}")
    for result in search_results:
        text_object.textLine(result)
    c.drawText(text_object)
    c.save()

    # Merge the original NLP analysis PDF and the new search results PDF
    merged_pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], f"NLP_analysis_enhanced_{original_filename}.pdf")
    output = PdfFileWriter()

    # Read the original NLP analysis PDF
    with open(os.path.join(app.config['UPLOAD_FOLDER'], f"NLP_analysis_{original_filename}.pdf"), "rb") as f:
        reader = PdfFileReader(f)
        for page in range(reader.getNumPages()):
            output.addPage(reader.getPage(page))

    # Read the new search results PDF
    with open(search_results_pdf_path, "rb") as f:
        reader = PdfFileReader(f)
        for page in range(reader.getNumPages()):
            output.addPage(reader.getPage(page))

    # Write the merged PDF
    with open(merged_pdf_path, "wb") as f:
        output.write(f)

    return jsonify({"status": "Enhancement complete", "enhanced_pdf": merged_pdf_path})
