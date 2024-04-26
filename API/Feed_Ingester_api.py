import requests
from pymongo import MongoClient
import gridfs
from bson import ObjectId
import pdfplumber

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client["Smart_Doc"]
fs = gridfs.GridFS(db)
api_key = ''  

# retrieves the analyzed text from the database
def get_file_content_from_db(file_id):
    try:
        file_id = ObjectId(file_id)
        file = fs.get(file_id)
        if file.content_type == 'text/plain':
            content = file.read().decode('utf-8')
        elif file.content_type == 'application/pdf':
            with pdfplumber.open(file) as pdf:
                pages = [page.extract_text() for page in pdf.pages if page.extract_text()]
                content = ' '.join(pages)
        else:
            return None, "Unsupported file type for analysis: {}".format(file.content_type)
        return content, file.filename
    except Exception as e:
        return None, f"Error retrieving file: {str(e)}"

# use chatgpt api to generate 2 keywords from the nlp_analysis text
def extract_keywords_with_chatgpt(text, api_key, num_keywords=2):
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': [{'role': 'system', 'content': f'Generate {num_keywords} key words and separate them using a comma:'},
                     {'role': 'user', 'content': text}],
        'max_tokens': 100  # Adjust token count if necessary
    }
    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
    if response.status_code == 200:
        keywords = response.json()['choices'][0]['message']['content'].strip().split(', ')
        return keywords
    else:
        return [], f"Failed to generate keywords, status code {response.status_code}, response: {response.text}"

google_api_key = ''
search_engine_id = ''

# use google custon search json api to search for the key words and return top 3 links for each key word
def google_search(query):
    url = f"https://www.googleapis.com/customsearch/v1?key={google_api_key}&cx={search_engine_id}&q={query}"
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json()
        links = [item['link'] for item in results.get('items', [])[:3]]
        return links
    else:
        print(f"Failed to fetch search results: {response.status_code} {response.text}") 
        return []


def main():
    file_id = input("Enter the file_id of the document to analyze: ")
    content, error = get_file_content_from_db(file_id)
    if content is None:
        print(f"Failed to retrieve the document: {error}")
        return

    keywords = extract_keywords_with_chatgpt(content, api_key)
    for keyword in keywords:
        print(f"Extracted keyword: {keyword}")
        links = google_search(keyword)
        if links:
            print(f"Top 3 relevant links for '{keyword}':")
            for link in links:
                print(link)
        else:
            print("No links found for the keyword.")

if __name__ == '__main__':
    main()
