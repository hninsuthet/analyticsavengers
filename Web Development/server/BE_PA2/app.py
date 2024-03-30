from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from data_cleaning_main import full_data_clean
from data_analysis_main import full_data_analysis
import uuid

DEBUG = True

app = Flask(__name__)

FLASK_1_URL = 'http://127.0.0.1:3000'

@app.route('/')
def home():
    return "Hello world from server 2."

app.config.from_object(__name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

CORS(app, resources={r'/*': {'origins': '*'}})
ALLOWED_EXTENSIONS = set(['csv', 'xlsx', 'json'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route to clean data
cleaned_data_storage = {}
analysed_data_storage = {}

@app.route('/cleandata', methods=['POST'])
def clean_data():
    file = request.files['file']
    filename = file.filename

    # Generate a unique key for this data
    data_key = str(uuid.uuid4())

    # Store the file data temporarily
    cleaned_data_storage[data_key] = file.read()

    cleaned_df, cleaning_time_info, rows_before_cleaning, duplicates_before_cleaning, nullvalues_before_cleaning, rows_after_cleaning, duplicates_after_cleaning, nullvalues_after_cleaning = full_data_clean(filename, file)
    # print(cleaned_data.info())
    # print(cleaned_data['InvoiceDate'].unique())
    # print(cleaned_data['InvoiceDate'])
    # Store the cleaned data temporarily
    cleaned_data_storage[data_key + '_cleaned'] = cleaned_df.to_json(orient='records')

    # Return the key for the client to retrieve the cleaned data
    return (
        jsonify({
            "data_key": data_key,
            "cleaning_time_info": cleaning_time_info,
            "rows_before_cleaning": rows_before_cleaning, 
            "duplicates_before_cleaning": duplicates_before_cleaning, 
            "nullvalues_before_cleaning": nullvalues_before_cleaning, 
            "rows_after_cleaning": rows_after_cleaning, 
            "duplicates_after_cleaning": duplicates_after_cleaning, 
            "nullvalues_after_cleaning": nullvalues_after_cleaning
        }), 200
    )


@app.route('/get_cleaned_data/<data_key>', methods=['GET'])
def get_cleaned_data(data_key):
    # Check if the data key exists
    if data_key in cleaned_data_storage and data_key + '_cleaned' in cleaned_data_storage:
        # Retrieve the cleaned data from storage
        cleaned_data_json = cleaned_data_storage[data_key + '_cleaned']
        # print(cleaned_data_json)
        return cleaned_data_json, 200
    else:
        return jsonify({"error": "No cleaned data available for the provided key"}), 404


@app.route('/analysedata', methods=['GET', 'POST'])
def analyse_data():
    file = request.files['file']
    filename = file.filename

    # Generate a unique key for this data
    data_key = str(uuid.uuid4())

    # Store the file data temporarily
    analysed_data_storage[data_key] = file.read()

    cleaned_data, cleaning_time_info, rows_before_cleaning, duplicates_before_cleaning, nullvalues_before_cleaning, rows_after_cleaning, duplicates_after_cleaning, nullvalues_after_cleaning = full_data_clean(filename, file)
    analysed_data = full_data_analysis(cleaned_data)
    # print(analysed_data) # output is in this format: 0\x10\x00\x08\x01
    # Store the analysed data temporarily
    analysed_data_storage[data_key + '_analysed'] = analysed_data
    # print(analysed_data_storage)

    return jsonify({"data_key": data_key}), 200


@app.route('/get_analysed_data/<data_key>', methods=['GET'])
def get_analysed_data(data_key):
    # Check if the data key exists
    if data_key in analysed_data_storage and data_key + '_analysed' in analysed_data_storage:
        # Retrieve the cleaned data from storage
        analysed_data_json = analysed_data_storage[data_key + '_analysed']
        # print(cleaned_data_json)
        return analysed_data_json, 200
    else:
        return jsonify({"error": "No analysed data available for the provided key"}), 404


if __name__ == '__main__':
    app.run(debug=True, port=3001)