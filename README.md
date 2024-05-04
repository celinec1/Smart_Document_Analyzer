# Smart_Document_Analyzer

Smart Doc offers the capability to save and parse PDF and TXT documents for specific keywords and phrases tailored to user interests. Users are required to log in or register with a unique username, ensuring no duplication. Leveraging OpenAI, it generates concise summaries and generates a NLP sentiment anaylsis, while Google Search integration fetches supplementary websites and sources to enrich these summaries. Additionally, the program provides links to these sources, offering users direct insights into the origin of the supplementary information.

## File Structure

### API
Contains 5 RESTful APIs that serve the main functions of this application:

- **Authorization_Authentication_api.py**: Manages user authentication and authorization processes. All the passwords in hashed before storing into the database. There are 4 functions contained in this file, validate_username(password), validate_password(password), login(usernmae, password), and create_account(username, password). This contains data protection to make sure that adversaries do not try to get access to another person's account using SQL injections.
  
- **Feed_Ingester_api.py**: Finds the keywords in the text and provides additional and relevant links using OpenAI and Google Custon Search JSON API. There are 3 functions in this file, get_file_content_from_db(fild_id), extract_keywords_with_chatgpt(text), and google_search(query). First OpenAI API is used to find the keywords by requesting the API to generate the keywords, then those keywords are parsed into singular words and prompt into the Google Custon Search JSON API to return top 3 relevant links.
  
- **Output_Generator_api.py**: Originally, this program constructed an analysis PDF based after the analysis on the uploaded text was complete. However, for styling reasons in the front-end this function was not used. Though, it served its purpose during the isolated backend testing.
  
- **Secure_File_Uploader_api.py**: Provides a secure way to upload documents to the system. As well as file management, since the user is able to create their own folders to put their files in. There are 5 functions in this program, allowed_file(filename), upload_file_to_db(file_stream, filenmame, content_type), get_file_from_db(file_id, download_path), delete_file_from_db(username, folder_name, file_id),create_folder(username, folder_name). The functions worked independently and are called in app.py when using Flask to connect the functionalities in the backend to the frontend.
  
- **Text_NLP_Analysis_api.py**: Performs Natural Language Processing (NLP) analysis and a smart summary on the text extracted from documents. There are 4 functions in this program, get_file_content_from_db(file_id), summarize_text_with_chatgpt(text), nlp_analysis(text), store_summary_in_db(username, folder_name, original_filename, summary). The get_file_content_from_db fetches the data the user selects and is gets the parsed text. Then summarize_text_with_chatgpt, provides the smart summary of the uploaded file. NLP_analysis generates another analysis for the user that is different from the summary. And the other functions are pretty clear in the name, they are all manipulating and accessing the db I created using Mongodb.

### app (frontend)

folder schema
app
  - app.py
  - templates
      - analyze.html : displays the analyzed summary, NLP analysis, keywords and links generated from the uploaded file
      - documents.html : displays the documents in the specific folder the user clicked on 
      - folder_files.html : displays the folders in the user's account
      - index.html : displays the home page where the user has to login or register
  - static
      - app.js : Flask and different callings of the backend functions so the frontend is connected to the backend
      - folder-icon.png

Overall, since all my functions were modular, I was able to call the specific functions that I needed to implement in the front end. The hardest part was trying to understand how to write html and JavaScript and make sure the html and JavaScript files were compatiable and executing the functions correctly.

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
          "analysis": "string of analysis"
          "NLP": "nlp string"
          "keywords and links": "string of the keywords and links"
        }
      ]
    }
  ]
}



### Demo 
<img width="1508" alt="Screenshot 2024-05-04 at 3 12 29 AM" src="https://github.com/celinec1/Smart_Document_Analyzer/assets/99696770/20e8e607-d24c-459f-9b7e-6f65d144e817">
This is the starting page, the user can either Login or Register and create and account

<img width="1502" alt="Screenshot 2024-05-04 at 3 12 46 AM" src="https://github.com/celinec1/Smart_Document_Analyzer/assets/99696770/f1f8645a-9cde-4059-8914-5c1b7a32e5d3">
When the user logs in they see their documents. These are the folders that are currently in their account 

<img width="1506" alt="Screenshot 2024-05-04 at 3 13 13 AM" src="https://github.com/celinec1/Smart_Document_Analyzer/assets/99696770/656c3455-08d5-40a9-a800-7acad7d7d6b3">
As shown here, if the user first registers there are no folders in their account

<img width="1227" alt="Screenshot 2024-05-04 at 3 19 12 AM" src="https://github.com/celinec1/Smart_Document_Analyzer/assets/99696770/56d67135-a278-4d15-91ab-6cf7ffb4c8d9">
When the user clicks on the folder, they are able to upload a document

<img width="1230" alt="Screenshot 2024-05-04 at 3 19 23 AM" src="https://github.com/celinec1/Smart_Document_Analyzer/assets/99696770/6f0db26b-3ad3-47b9-a6bd-ddd4b027cfe5">
This is the generated analysis for the above document about AI Chips Behind Nvidia

Quick Video Demo: https://drive.google.com/file/d/1ao7aeDuE_LCu3NpGrFAoSn7u6h3pXyHa/view?usp=sharing



### Queue Implementation:
Implements a queue for managing the processing of NLP analysis and secure file uploads. This ensures efficient handling of tasks and scalability of the system.

### Docker/front-end for now ~until I implement and add frontend :) ~ (The proof of concept phase)
1. <img width="332" alt="Screenshot 2024-03-24 at 10 51 41 PM" src="https://github.com/celinec1/Smart_Document_Analyzer/assets/99696770/902f7635-15e6-4785-8001-337c19fe7a7e">


2. <img width="370" alt="Screenshot 2024-03-24 at 10 51 45 PM" src="https://github.com/celinec1/Smart_Document_Analyzer/assets/99696770/b4bb69cb-4023-459d-a1b9-f2b7244a7d02">


3. <img width="392" alt="Screenshot 2024-03-24 at 10 51 50 PM" src="https://github.com/celinec1/Smart_Document_Analyzer/assets/99696770/b620b8c6-b687-46d7-b338-1e3722825e13">


### Instructions for Developers

1. Clone the repository to your local environment.
2. Install the required dependencies specified in requirements.txt and run dockerfile
3. Install Mongodb
4. Run app.py in the app folder
5. Put in API keys to ensure OpenAI and Google Search Custon JSON API can run
6. Open your web browser at http://127.0.0.1:5000

### Summary:
Overall, I learned a lot from this project, especially about how to efficiently use APIs and create modular functions. This was a significant takeaway for me, as I had not previously written isolated backend code and then connected it with the frontend. One of the toughest challenges I faced was the high modularity, which made me feel like I was creating unnecessary functions and files in the frontend, requiring extensive imports of libraries and components in JavaScript. However, as we learned in EC530, not all code is used—software developers often write more code than is actually needed. Given more time, I would explore React libraries like Tailwind to create a more captivating frontend. Additionally, I plan to integrate more APIs into this project, such as text-to-speech capabilities to enhance accessibility and ease of use.
