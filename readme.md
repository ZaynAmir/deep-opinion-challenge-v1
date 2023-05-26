# Deep Opinion

This project is a Python Django application using SQLite as the database. It is designed to provide a brief introduction and guide on how to set up and run the project locally.

## Considerations

During the development of this code challenge, I made several decisions to ensure the efficiency, reliability, and maintainability of the code. Here are the principal decisions I made and the reasons behind them:

1. SQLite Database: I chose SQLite as the database for this project. SQLite is a lightweight, serverless, and file-based database that is widely supported and easy to set up. Since this project is intended to be simple and self-contained, SQLite provides a suitable choice without the need for additional database installations or configurations.

2. Django and Django Rest Framework: Django is a high-level Python web framework known for its robustness and extensive built-in features. I chose Django for this project due to its ability to handle database operations, provide an ORM (Object-Relational Mapping) layer for seamless database integration, and simplify the development of RESTful APIs. Django Rest Framework builds upon Django, providing powerful tools and utilities for building web APIs and serialization.

3. Pandas: Pandas is a popular library in the Python ecosystem for data manipulation and analysis. Pandas is used to handle CSV and Excel file processing. It offers convenient methods for reading different file formats into data structures, such as DataFrames, enabling easy data extraction and transformation. By leveraging Pandas, we can efficiently read and process file data before storing it in the database.

4. Database Optimization in Upload Sheet API: To optimize the database performance during the insertion process in the Upload Sheet API, several techniques are employed. These techniques include increasing the cache size, setting the journaling mode to memory, disabling indexing while inserting, setting the synchronous mode to OFF, disabling change counting, and using memory for temporary storage. These optimizations aim to reduce disk I/O, enhance write operations, and improve the overall performance of the database.

5. Atomic Transactions: Atomic transactions are utilized in the Create Tag API. By using atomic transactions, we ensure that the creation of a new tag and its association with the training data entry are treated as a single, indivisible operation. If an exception occurs during the process, the transaction will be rolled back, maintaining data integrity and preventing partial or inconsistent data.

6. Redis is a popular in-memory data store often used for caching and improving performance in web applications. Redis can be used to cache frequently accessed data or query results, reducing the database load and improving response times. When a request is made to download a tagged sheet, i check if the corresponding data is already present in the Redis cache. If it is, retrieve the cached response and return it. This avoids the need to fetch the data from the database again.

## Prerequisites

To run this project, you need to have the following installed on your system:

Python (version > 3.9)
Django (version 4.2.1)
SQLite (version 3.42.0)
djangorestframework(version 3.14.0)

## Installation

Clone the repository to your local machine (private-repo).
command:
git clone https://github.com/ZaynAmir/deep-opinion-challenge-v1.git

Navigate to the source directory and install the requirements.txt.
command:
pip install -r requirements.txt

## Database Configuration

This project uses SQLite as the database. SQLite is already included with Python, so no additional installation is required. The default database settings are already configured to use SQLite.

## Setting Up the Database

To create the necessary tables and set up the database, follow these steps:

1. Apply the database migrations.
   command:
   python manage.py migrate

2. (Optional) Load initial data (if available).
   command:
   python manage.py loaddata data.json

## Running the Application

To start the development server and run the application, execute the following command:
command:
python manage.py runserver

## Usage

After starting the development server, you can access the application and perform the following actions:

Action 1: [upload the file in csv or xlsx]

Action 2: [tag or label data that was uploaded]

Action 3: [update tags sentiment or aspects or both]

Action 4: [get all aspects from a specific uploaded sheet]

Action 5: [get all sentiments from a specific uploaded sheet]

Action 6: [get all labeled/taged data with the api]

Action 7: [download labeled/taged xlsx file with the download-sheet api]

## File Upload API

This project contains an API endpoint for uploading files (CSV or Excel) and inserting the data into an SQLite database table.

### API Endpoint

POST localhost:8000/api/v1/upload

Request
The API endpoint expects a multipart/form-data request with the following parameters:

file (file): The file to be uploaded. Only CSV and Excel file formats are supported.

### Response

1. HTTP 201 Created: The file was successfully uploaded and the data was inserted into the database. The response body will contain the following JSON object:
   {
   "success": true,
   "sheet_id": <sheet_id>,
   "message": "<file_name> uploaded."
   }

2. HTTP 400 Bad Request: The file format is invalid. Only CSV and Excel files are supported. The response body will contain the following JSON object:
   {
   "error": "Invalid file format"
   }

3. HTTP 500 Internal Server Error: An internal server error occurred during the upload process. The response body will contain the following JSON object:
   {
   "error": "Internal Server Error"
   }

## Create Tag API

This project contains an API endpoint for creating tags on a row of text that was uploaded.

### API Endpoint

POST localhost:8000/api/v1/create-tag

Request
The API endpoint expects a JSON payload with the following parameters:

aspect (string): The aspect to be tagged.
sentiment (string): The sentiment associated with the aspect. Only "POS", "NEG", or "NEU" are allowed.
text_id (integer): The ID of the training data entry to which the tag should be associated.
like this:
{
"text_id": "<text_id>",
"sentiment": "POS",
"aspect": "some aspect"
}

### Response

The API response will vary depending on the success or failure of the tag creation process. Possible responses are:

1. HTTP 201 Created: The tag was successfully created and associated with the training data entry. The response body will contain the following JSON object:
   {
   "success": true,
   "tag_id": <tag_id>,
   "message": "Tag is created"
   }
