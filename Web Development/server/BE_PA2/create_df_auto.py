import pandas as pd
from fuzzywuzzy import process
import difflib

# ## Function that creates a dataframe for summary stats
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
# Function that creates a dataframe for clv analysis
def get_clv_df(df):
    # Get a list of all the columns in the dataframe
    columns = df.columns

    # Columns that are needed for the calculations of CLV 
    clv_columns = ['CustomerID', 'UnitPrice', 'Quantity', 'InvoiceDate']

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

# Function that creates a dataframe for customer profiling analysis
def get_profiling_df(df):
    # Get a list of all the columns in the dataframe
    columns = df.columns

    # Columns that are needed for the calculations of CLV 
    profiling_columns = ['CustomerID', 'Description','UnitPrice', 'Quantity', 'Country', 'Gender', 'Category']

    # Iterate through each required column and find the best match
    for i, column in enumerate(profiling_columns):
        if column not in columns:
            # Use fuzzy matching to find the best match
            best_match, score = process.extractOne(column, columns)
            if score < 80:  # Adjusted threshold for a better match
                # If the best match score is below a certain threshold, try difflib
                best_match = difflib.get_close_matches(column, columns, n=1, cutoff=0.8)
                if best_match:
                    profiling_columns[i] = best_match[0]
                else:
                    raise ValueError(f"No good match found for column '{column}'")
            else:
                profiling_columns[i] = best_match
        else:
            # If it's an exact match, keep the original column name
            profiling_columns[i] = column

    # Create a new DataFrame with only the required columns
    profiling_df = df[profiling_columns].copy()
    
    return profiling_df

# Function that creates a dataframe for strategy analysis
def get_strategy_df(df):
    # Get a list of all the columns in the dataframe
    columns = df.columns

    # Columns that are needed for the calculations of strategy analysis
    strategy_columns = ['CustomerID','InvoiceNo', 'StockCode','Description', 'InvoiceDate','UnitPrice', 'Quantity', 'Country', 'Gender', 'Category']

    # Iterate through each required column and find the best match
    for i, column in enumerate(strategy_columns):
        if column not in columns:
            # Use fuzzy matching to find the best match
            best_match, score = process.extractOne(column, columns)
            if score < 80:  # Adjusted threshold for a better match
                # If the best match score is below a certain threshold, try difflib
                best_match = difflib.get_close_matches(column, columns, n=1, cutoff=0.8)
                if best_match:
                    strategy_columns[i] = best_match[0]
                else:
                    raise ValueError(f"No good match found for column '{column}'")
            else:
                strategy_columns[i] = best_match
        else:
            # If it's an exact match, keep the original column name
            strategy_columns[i] = column

    # Create a new DataFrame with only the required columns
    strategy_df = df[strategy_columns].copy()
    
    return strategy_df

def get_unique_products_df(df):
    # Get a list of all the columns in the dataframe
    columns = df.columns

    # Columns that are needed for getting unique products
    products_columns = ['Description', 'UnitPrice', 'Category']

    # Iterate through each required column and find the best match
    for i, column in enumerate(products_columns):
        if column not in columns:
            # Use fuzzy matching to find the best match
            best_match, score = process.extractOne(column, columns)
            if score < 80:  # Adjusted threshold for a better match
                # If the best match score is below a certain threshold, try difflib
                best_match = difflib.get_close_matches(column, columns, n=1, cutoff=0.8)
                if best_match:
                    products_columns[i] = best_match[0]
                else:
                    raise ValueError(f"No good match found for column '{column}'")
            else:
                products_columns[i] = best_match
        else:
            # If it's an exact match, keep the original column name
            products_columns[i] = column

    # Create a new DataFrame with only the required columns
    df_productList = df[products_columns].copy()

    # Drop duplicates based on 'Description' while keeping the first occurrence
    unique_products_df = df_productList.drop_duplicates(subset=['Description'], keep='first')
    
    return unique_products_df
