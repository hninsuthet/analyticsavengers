import pandas as pd 
import numpy as np
import datetime as dt

from create_clv_tiers_df import get_clv_tiers
from summary_statistics import generate_sales_trends


def get_monthly_clv(df):

    # get clv df
    clv_df = get_clv_tiers(df)

     # Drop the columns that are not needed in the original df
    df = df.drop(["InvoiceNo", "StockCode", "Description", "Category", "Country", "Gender"], axis=1)

    # Rearrange the columns in the original df
    df = df[['CustomerID', 'Quantity', 'UnitPrice', 'InvoiceDate']]

    # Convert 'InvoiceDate' to datetime type if it's not already
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    
    # Add a new column for the month in the original df
    df['Month'] = df['InvoiceDate'].dt.strftime('%b %Y')

    # Merge the original df with the clv_df - add columns CLV and Tier to the original df
    merged_df = pd.merge(df, clv_df[['CustomerID', 'CLV', 'Tier']], on='CustomerID', how='inner')

    # Group the merged df by month and calculate the average CLV for each month
    merged_df_grouped1 = merged_df.groupby('Month').agg({'CLV': 'mean'}).reset_index()

    # Group the merged df by month and tier and calculate the number of customers in each tier for each month
    merged_df_grouped2 = merged_df.groupby(['Month', 'Tier']).agg({ 'CustomerID': 'nunique'}).reset_index()

    # Merge the two grouped dfs
    merged_df_combined = pd.merge(merged_df_grouped1, merged_df_grouped2, on='Month', how='inner')
    # Rename the columns for the final merged df
    merged_df_combined.rename(columns={'CustomerID': 'Number of Customers in each Tier', 'CLV': 'Average CLV'}, inplace=True)

    # Pivot the DataFrame
    pivot_df = merged_df_combined.pivot_table(index='Month', columns='Tier', values=['Average CLV', 'Number of Customers in each Tier'], aggfunc='first')

    # Flatten the MultiIndex columns
    pivot_df.columns = [f"{col[1]}_{col[0]}" for col in pivot_df.columns]

    # Reset index to make 'Month' a column again
    pivot_df.reset_index(inplace=True)

    # Drop columns and rename columns
    pivot_df = pivot_df.drop(['High Tier CLV_Average CLV', 'Medium Tier CLV_Average CLV'], axis=1)
    pivot_df.rename(columns={'Low Tier CLV_Average CLV': 'Average_CLV', 
                             'High Tier CLV_Number of Customers in each Tier': 'High_Tier', 
                             'Medium Tier CLV_Number of Customers in each Tier': 'Middle_Tier', 
                             'Low Tier CLV_Number of Customers in each Tier': 'Low_Tier'}, inplace=True)
    
    # get monthly sales df
    sales_df = generate_sales_trends(df)

    # Merge the sales_df with the pivot_df
    pivot_df = pd.merge(pivot_df, sales_df, on='Month', how='inner')

    return pivot_df