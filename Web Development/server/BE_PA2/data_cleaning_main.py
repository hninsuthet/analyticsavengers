import pandas as pd
import time
# from textblob import TextBlob

# Reading file
def read_file(filename, file):
    file_extension = filename.split(".")[-1]

    if file_extension in ['xls' , 'xlsx' , 'xlsm' , 'xlsb' , 'odf' , 'ods' , 'odt']:
        df = pd.read_excel(file)
        return df
    
    elif file_extension == 'csv':
        df = pd.read_csv(file)
        return df
    
    elif file_extension == 'json':
        df = pd.read_json(file)
        return df

# Detect unique identifiers in the dataset that CANNOT be imputed, or interpolated
def detect_unique_identifiers(df):
    unique_identifier = []

    id_list = df.columns.str.contains('code|number|no|sku|id|ids|uid', case=False)
    for i in range(len(id_list)):
        if id_list[i] == True:
            unique_identifier.append(df.columns[i])

    for column in df.columns:
        if df[column].nunique() == df.shape[0]:
            unique_identifier.append(column)

    return unique_identifier

# Duplicates & Null Values
def remove_duplicates(df):
    # Remove duplicates and create a new DataFrame
    df_cleaned = df.drop_duplicates()

    return df_cleaned

def handle_null_values(df):

    # Count null values in each column
    null_counts = df.isnull().sum()

    # Calculate the percentage of null values for each column
    null_percentages = (null_counts / len(df)) * 100

    # Identify columns with non-zero null percentages
    columns_to_handle = null_percentages[null_percentages > 0].index

    # Create a copy of the original DataFrame
    clean_df = df.copy()

    # Rule 1: Remove rows with less than 5% missing values + remove rows with missing values in unique identifiers
    clean_df = clean_df.dropna(subset=columns_to_handle[null_percentages[columns_to_handle] < 5].tolist())
    clean_df = clean_df.dropna(subset=detect_unique_identifiers(clean_df))
    
    # Check if there are any rows left
    if len(clean_df) == 0:
        return clean_df  # No need to proceed if all rows were removed

    # Rule 2: Impute mean or mode for columns with 5-20% missing values
    for col in columns_to_handle:
        if (null_percentages[col] >= 5) and (null_percentages[col] <= 20):
            if pd.api.types.is_numeric_dtype(clean_df[col]):
                clean_df[col].fillna(clean_df[col].mean(), inplace=True)
            else:
                clean_df[col].fillna(clean_df[col].mode().iloc[0], inplace=True)

    # Rule 3: Linear Interpolation for numeric columns and mode for non-numeric columns for 20-40% missing values
    for col in columns_to_handle:
        if (null_percentages[col] > 20) and (null_percentages[col] < 40):
            if pd.api.types.is_numeric_dtype(clean_df[col]):
                clean_df[col] = clean_df[col].interpolate(method='linear')
            else:
                clean_df[col].fillna(clean_df[col].mode().iloc[0], inplace=True)

    # Rule 4: Drop columns with more than 40% missing values
    clean_df = clean_df.drop(columns=columns_to_handle[null_percentages[columns_to_handle] >= 40])

    return clean_df

# TextBlob Spelling Correction Function
# def correct_spelling(text):
#     blob = TextBlob(text)
#     return str(blob.correct())

# Standardization Function for text - Capitalize first letter of every word
def standardize_text(text):
    return str(text).title()

# Standardize Date to datetime format
def standardize_dates(series):
    pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}|\d{4}-\d{2}-\d{2}|\d{4}/\d{2}/\d{2}|\d{8}|\d{2}-\d{2}-\d{4}'
    if series.astype(str).str.match(pattern).any():
        series = pd.to_datetime(series, errors='coerce')
    return series

def clean_data(df):
    # Identify text columns
    text_columns = df.select_dtypes(include=['object']).columns

    # Standardize text 
    df[text_columns] = df[text_columns].apply(lambda x: x.apply(standardize_text) if not x.astype(str).str.contains(r'\d').all() else x)

    # Spelling Correction 
    # df[text_columns] = df[text_columns].apply(lambda x: x.apply(correct_spelling) if not x.astype(str).str.contains(r'\d').any() else x)

    # Standardize dates
    df = df.apply(standardize_dates)

    # Splitting date
    datetime_columns = df.select_dtypes(include=['datetime', 'datetime64', 'datetime64[ns]']).columns
    
    for column in datetime_columns:
        df[column] = df[column].dt.strftime('%Y-%m-%d') ## changed from dt.date due to json string reads date as 1291161600000
        
    return df

# For providing cleaned data
def full_data_clean(filename, file): # remove argument: output_excel
    print("Processing data cleaning ...")
    
    # Initialise the start of processing time
    start_time = time.time()

    # Calculate the processing time
    time1 = time.time()
    reading_time = time1 - start_time
    reading_time_minutes = int(reading_time // 60)
    reading_time_seconds = int(reading_time % 60)

    # Read user file into a DataFrame
    df = read_file(filename, file)

    # Evaluate metrics before cleaning
    rows_before_cleaning = {"Number of Rows Before Cleaning": len(df)}
    duplicates_before_cleaning = {"Number of Duplicates Before Cleaning": int(df.duplicated().sum())}
    nullvalues_before_cleaning = { "Number of Null Values Before Cleaning": df.isnull().sum().astype(int).to_dict()}

    print(rows_before_cleaning)
    print(duplicates_before_cleaning)
    print(nullvalues_before_cleaning)

    # Apply the cleaning functions
    cleaned_df = remove_duplicates(df)
    print('Done removing duplicates')

    cleaned_df = handle_null_values(cleaned_df)
    print('Done handling null values')
    
    cleaned_df = clean_data(cleaned_df)
    print("Done cleaning data ...")

    # Calculate the processing time
    time2 = time.time()
    cleaning_time = time2 - time1
    cleaning_time_minutes = int(cleaning_time // 60)
    cleaning_time_seconds = int(cleaning_time % 60)
    cleaning_time_info =  f"Processing Time: {cleaning_time_minutes} minutes {cleaning_time_seconds} seconds"
    print(cleaning_time_info)

    # Evaluate metrics after cleaning
    rows_after_cleaning = { "Number of Rows After Cleaning": len(cleaned_df)}
    duplicates_after_cleaning = { "Number of Duplicates After Cleaning": int(cleaned_df.duplicated().sum())}
    nullvalues_after_cleaning = { "Number of Null Values After Cleaning": cleaned_df.isnull().sum().astype(int).to_dict()}

    print(rows_after_cleaning)
    print(duplicates_after_cleaning)
    print(nullvalues_after_cleaning)

    # return cleaned_df, cleaning_time_info, rows_before_cleaning, duplicates_before_cleaning, nullvalues_before_cleaning, rows_after_cleaning, duplicates_after_cleaning, nullvalues_after_cleaning
    return cleaned_df
