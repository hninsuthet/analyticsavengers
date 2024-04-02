import pandas as pd

from create_df_auto import get_stats_df

def generate_sales_trends(df):

    # Get stats df 
    stats_df = get_stats_df(df)

    # Ensure 'InvoiceDate' column is in datetime format
    stats_df['InvoiceDate'] = pd.to_datetime(stats_df['InvoiceDate'])
    
    # Extract month and year from the 'InvoiceDate' column
    stats_df['Month'] = stats_df['InvoiceDate'].dt.strftime('%b %Y')  # Extracting month and year
    
    # Calculate Total Sales
    stats_df['Total_Sales'] = stats_df['Quantity'] * stats_df['UnitPrice']
    
    # Group by month and sum sales
    monthly_sales = stats_df.groupby('Month')['Total_Sales'].sum()

    # Convert monthly_sales to a dataframe 
    monthly_sales_data = monthly_sales.reset_index(name='Monthly_Sales')
        
    return monthly_sales_data