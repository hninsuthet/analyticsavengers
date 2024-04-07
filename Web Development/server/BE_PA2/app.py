from flask import Flask, request
from flask_cors import CORS
import os
from data_cleaning_main import full_data_clean
from data_analysis_main import full_data_analysis

DEBUG = True

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello from server 2."

app.config.from_object(__name__)

CORS(app, resources={r'/*': {'origins': '*'}})
ALLOWED_EXTENSIONS = set(['csv', 'xlsx', 'json'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/cleandata', methods=['POST'])
def clean_data():
    file = request.files['file']
    filename = file.filename
    cleaned_df = full_data_clean(filename, file)
    cleaned_df = cleaned_df.to_json(orient='records')

    return (cleaned_df, 200)


@app.route('/analysedata', methods=['POST'])
def analyse_data():
    file = request.files['file']
    filename = file.filename
    cleaned_data = full_data_clean(filename, file)
    analysed_data = full_data_analysis(cleaned_data)

    return (analysed_data, 200)

if __name__ == '__main__':
    app.run(debug=True, port=3001)