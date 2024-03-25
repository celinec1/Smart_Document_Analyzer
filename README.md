# Smart_Document_Analyzer

Smart_Document_Analyzer will be able to save and parse through PDF documents for keywords and phrases the user is looking for. After finding its occurrences in the document, it will complete text analysis.

## File Structure

### API
Contains 5 RESTful APIs that serve the main functions of this application:

- **Authorization_Authentication_api.py**: Manages user authentication and authorization processes.
- **Feed_Ingester_api.py**: Handles the ingestion of documents into the system for processing.
- **Output_Generator_api.py**: Generates output based on the analysis performed on the documents.
- **Secure_File_Uploader_api.py**: Provides a secure way to upload documents to the system.
- **Text_NLP_Analysis_api.py**: Performs Natural Language Processing (NLP) analysis on the text extracted from documents.

### Database
Utilizes MongoDB for storing user data, document metadata, and analysis results. Below is a sample implementation of user and document management within the database:

Database schema:
{
  "username": "celine",
  "password": "<hashed_password>",
  "folders": [
    {
      "folder_name": "MyDocuments",
      "files": [
        {
          "file_name": "example.pdf",
          "analysis": "PDF analysis"
        }
      ]
    }
  ]
}

### Queue Implementation:
Implements a queue for managing the processing of NLP analysis and secure file uploads. This ensures efficient handling of tasks and scalability of the system.

### Docker/front-end for now ~until I implement and add frontend :) ~
1. <img width="332" alt="Screenshot 2024-03-24 at 10 51 41 PM" src="https://github.com/celinec1/Smart_Document_Analyzer/assets/99696770/902f7635-15e6-4785-8001-337c19fe7a7e">


2. <img width="370" alt="Screenshot 2024-03-24 at 10 51 45 PM" src="https://github.com/celinec1/Smart_Document_Analyzer/assets/99696770/b4bb69cb-4023-459d-a1b9-f2b7244a7d02">


3. <img width="392" alt="Screenshot 2024-03-24 at 10 51 50 PM" src="https://github.com/celinec1/Smart_Document_Analyzer/assets/99696770/b620b8c6-b687-46d7-b338-1e3722825e13">



