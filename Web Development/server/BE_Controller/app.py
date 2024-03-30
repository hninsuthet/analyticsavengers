from flask import Flask, jsonify, request, send_file, Response, session
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import requests
import pandas as pd
import json

DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = 'BAD_SECRET_KEY'

CORS(app, resources={r'/*': {'origins': '*'}})
ALLOWED_EXTENSIONS = set(['csv', 'xlsx', 'json'])

FLASK_2_URL = 'http://127.0.0.1:3001'

analysed_data_storage = {}

@app.route('/cleandata', methods=['GET', 'POST'])
def clean_data_from_client():
    if request.method == 'POST':
        file = request.files['file']
        
        # Send the file content to Flask 2 for cleaning
        response = requests.post(f'{FLASK_2_URL}/cleandata', files={'file': (file.filename, file)})
        
        if response.status_code == 200:
            # Cleaning done, now retrieve the cleaned data
            data_key = response.json().get('data_key')
            cleaned_data_response = requests.get(f'{FLASK_2_URL}/get_cleaned_data/{data_key}')
            if cleaned_data_response.status_code == 200:
                # Receive and process the cleaned data
                cleaned_data = cleaned_data_response.json()

                # Process cleaned data as needed
                # For example, save to CSV and return as download
                # Convert the dictionary data into a pandas DataFrame
                cleaned_data = pd.DataFrame(cleaned_data)
                # cleaned_data.to_excel('cleaned_data.xlsx', index=False)
                cleaned_data.to_csv('cleaned_data.csv', date_format='%Y-%m-%d', index=False)
                csv_data = cleaned_data.to_csv(date_format='%Y-%m-%d', index=False)
                return Response(
                    csv_data,
                    mimetype='text/csv',
                    headers={
                        "Content-disposition": f"attachment; filename=cleaned_data.csv"
                    }
                )
            else:
                return "Failed to retrieve cleaned data from Flask 2", 500
        else:
            return "Failed to send data to Flask 2", 500
    return "Hello from Flask 1"


@app.route('/dataanalysis', methods=['GET', 'POST'])
def analyse_data_from_client():
    if request.method == 'POST':
        file = request.files['file']
        
        # Send the file content to Flask 2 for cleaning
        response = requests.post(f'{FLASK_2_URL}/analysedata', files={'file': (file.filename, file)})
    
        if response.status_code == 200:
            # Analysis done, retrieve the analysed data
            data_key = response.json().get('data_key')
            session['id'] = data_key
            analysed_data_response = requests.get(f'{FLASK_2_URL}/get_analysed_data/{data_key}')
            if analysed_data_response.status_code == 200:
                # Receive and process the cleaned data
                analysed_data = analysed_data_response.json()
                analysed_data_storage[data_key] = analysed_data
                return jsonify({"data_key": data_key}), 200
            else:
                return "Failed to retrieve cleaned data from Flask 2", 500
        else:
            return "Failed to send data to Flask 2", 500
    return "Hello from Flask 1"

@app.route('/get_analysed_data/<data_key>', methods=['GET'])
def get_analysed_data(data_key):
    # Check if the data key exists
    if data_key in analysed_data_storage:
        # Retrieve the cleaned data from storage
        analysed_data_json = analysed_data_storage[data_key]
        return analysed_data_json, 200
    else:
        return jsonify({"error": "No analysed data available for the provided key"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=3000)