from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from data_cleaning_main import full_data_clean
from data_analysis_main import full_data_analysis

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

    # cleaned_df, cleaning_time_info, rows_before_cleaning, duplicates_before_cleaning, nullvalues_before_cleaning, rows_after_cleaning, duplicates_after_cleaning, nullvalues_after_cleaning = full_data_clean(filename, file)
    cleaned_df = full_data_clean(filename, file)
    cleaned_df = cleaned_df.to_json(orient='records')

    # return (
    #     jsonify({
    #         "cleaned_df": cleaned_df,
    #         "cleaning_time_info": cleaning_time_info,
    #         "rows_before_cleaning": rows_before_cleaning, 
    #         "duplicates_before_cleaning": duplicates_before_cleaning, 
    #         "nullvalues_before_cleaning": nullvalues_before_cleaning, 
    #         "rows_after_cleaning": rows_after_cleaning, 
    #         "duplicates_after_cleaning": duplicates_after_cleaning, 
    #         "nullvalues_after_cleaning": nullvalues_after_cleaning
    #     }), 200
    # )
    return (cleaned_df, 200)


@app.route('/analysedata', methods=['POST'])
def analyse_data():
    file = request.files['file']
    filename = file.filename

    # cleaned_data, cleaning_time_info, rows_before_cleaning, duplicates_before_cleaning, nullvalues_before_cleaning, rows_after_cleaning, duplicates_after_cleaning, nullvalues_after_cleaning = full_data_clean(filename, file)
    cleaned_data = full_data_clean(filename, file)
    analysed_data = full_data_analysis(cleaned_data)

    return (analysed_data, 200)

if __name__ == '__main__':
    app.run(debug=True, port=3001)