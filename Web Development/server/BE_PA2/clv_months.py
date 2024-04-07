import pandas as pd 

from create_rfmt_clv_tiers_df import get_clv_tiers
from create_df_auto import get_clv_df


def get_monthly_clv(df):

     # Get the extracted original DataFrame
     extracted_df = get_clv_df(df)
    
     # Calculate the total sales for each row
     extracted_df['Sales'] = extracted_df['Quantity'] * extracted_df['UnitPrice']

    # # Convert 'InvoiceDate' to '%Y-%m' format, eg. '2010-12'
     # Convert 'InvoiceDate' to '%Y-%m' format, eg. '2010-12-01'
     extracted_df['Month'] = pd.to_datetime(extracted_df['InvoiceDate']).dt.to_period('M')

    # Get CLV Tiers DataFrame
     clv_df = get_clv_tiers(df)

    # Merge the original df with the clv_df - add columns CLV and Tier to the original df
     merged_df = pd.merge(extracted_df, clv_df[['CustomerID', 'CLV', 'Tier']], on='CustomerID', how='inner')

    # Group the merged df by month and calculate the total revenue and average CLV for each month
     merged_df_grouped1 = merged_df.groupby('Month').agg({'Sales': 'sum','CLV': 'mean'}).reset_index()

    # Group the merged df by month and tier and calculate the number of customers in each tier for each month
     merged_df_grouped2 = merged_df.groupby(['Month', 'Tier']).agg({'CustomerID': 'nunique'}).reset_index()

    # Merge the two grouped dfs
     merged_df_combined = pd.merge(merged_df_grouped1, merged_df_grouped2, on='Month', how='inner')
    
    # Rename the columns for the final merged df
     merged_df_combined.rename(columns={'CustomerID': 'Number of Customers in each Tier', 'Sales': 'Total_Revenue', 'CLV': 'Average CLV', }, inplace=True)

    # Pivot the DataFrame
     pivot_df = merged_df_combined.pivot_table(index='Month', columns='Tier', values=['Average CLV', 'Number of Customers in each Tier', 'Total_Revenue'], aggfunc='first')

    # Flatten the MultiIndex columns
     pivot_df.columns = [f"{col[1]}_{col[0]}" for col in pivot_df.columns]

    # Reset index to make 'Month' a column again
     pivot_df.reset_index(inplace=True)

    # Drop columns and rename columns
     pivot_df = pivot_df.drop(['High Tier CLV_Average CLV', 'Middle Tier CLV_Average CLV', 'High Tier CLV_Total_Revenue', 'Middle Tier CLV_Total_Revenue'], axis=1)
     pivot_df.rename(columns={'Low Tier CLV_Total_Revenue': 'Total_Revenue',
                             'Low Tier CLV_Average CLV': 'Average_CLV', 
                             'High Tier CLV_Number of Customers in each Tier': 'High_Tier', 
                             'Middle Tier CLV_Number of Customers in each Tier': 'Middle_Tier', 
                             'Low Tier CLV_Number of Customers in each Tier': 'Low_Tier'}, inplace=True)

     return pivot_df