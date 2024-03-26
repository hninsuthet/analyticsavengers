import pandas as pd
from fuzzywuzzy import fuzz
import difflib

## Function that creates a dataframe for summary stats
def get_stats_df(df):
    # Get a list of all the columns in the dataframe
    columns = df.columns

    # Columns that are needed for the statistics DataFrame
    stats_columns = ['Quantity', 'UnitPrice', 'InvoiceDate', 'CustomerID']

    # Iterate through each required column and find the best match
    for i, column in enumerate(stats_columns):
        if column not in columns:
            # Use fuzzy matching to find the best match
            best_match, score = process.extractOne(column, columns)
            if score < 80:  # Adjusted threshold for a better match
                # If the best match score is below a certain threshold, try difflib
                best_match = difflib.get_close_matches(column, columns, n=1, cutoff=0.8)
                if best_match:
                    stats_columns[i] = best_match[0]
                else:
                    raise ValueError(f"No good match found for column '{column}'")
            else:
                stats_columns[i] = best_match
        else:
            # If it's an exact match, keep the original column name
            stats_columns[i] = column

    # Create a new DataFrame with only the required columns
    stats_df = df[stats_columns].copy()
    # Check if 'InvoiceDate' column is datetime type and convert if not
    if not pd.api.types.is_datetime64_any_dtype(stats_df['InvoiceDate']):
        stats_df['InvoiceDate'] = pd.to_datetime(stats_df['InvoiceDate'])

    return stats_df

## Function that creates a dataframe for clv
def get_clv_df(df):
    # Get a list of all the columns in the dataframe
    columns = df.columns

    # Columns that are needed for the calculations of CLV 
    clv_columns = ['InvoiceNo', 'CustomerID', 'UnitPrice', 'Quantity', 'InvoiceDate']

    # Iterate through each required column and find the best match
    for i, column in enumerate(clv_columns):
        if column not in columns:
            # Use fuzzy matching to find the best match
            best_match, score = process.extractOne(column, columns)
            if score < 80:  # Adjusted threshold for a better match
                # If the best match score is below a certain threshold, try difflib
                best_match = difflib.get_close_matches(column, columns, n=1, cutoff=0.8)
                if best_match:
                    clv_columns[i] = best_match[0]
                else:
                    raise ValueError(f"No good match found for column '{column}'")
            else:
                clv_columns[i] = best_match
        else:
            # If it's an exact match, keep the original column name
            clv_columns[i] = column

    # Create a new DataFrame with only the required columns
    clv_df = df[clv_columns].copy()
     # Check if 'InvoiceDate' column is datetime type and convert if not
    if not pd.api.types.is_datetime64_any_dtype(clv_df['InvoiceDate']):
        clv_df['InvoiceDate'] = pd.to_datetime(clv_df['InvoiceDate'])
           
    return clv_df

## Function that creates a dataframe for rfm
def get_rfm_df(df):
    # Required RFM columns
    rfm_columns = ['InvoiceNo', 'StockCode', 'Quantity', 'InvoiceDate', 
                   'UnitPrice', 'CustomerID', 'Country', 'Gender', 'Category']
    
    # Get a list of all the columns in the dataframe
    columns = set(df.columns)

    # Iterate through each required column and find the best match
    matched_columns = []
    for column in rfm_columns:
        if column not in columns:
            # Use fuzzy matching to find the best match
            best_match, score = process.extractOne(column, columns)
            if score < 80:  # Adjusted threshold for a better match
                # If the best match score is below a certain threshold, try difflib
                best_match = difflib.get_close_matches(column, columns, n=1, cutoff=0.8)
                if best_match:
                    matched_columns.append(best_match[0])
                else:
                    raise ValueError(f"No good match found for column '{column}'")
            else:
                matched_columns.append(best_match)
        else:
            # If it's an exact match, keep the original column name
            matched_columns.append(column)

    # Create a new DataFrame with only the required columns
    rfm_df = df[matched_columns].copy()
     # Check if 'InvoiceDate' column is datetime type and convert if not
    if not pd.api.types.is_datetime64_any_dtype(rfm_df['InvoiceDate']):
        rfm_df['InvoiceDate'] = pd.to_datetime(rfm_df['InvoiceDate'])
               
    return rfm_df
