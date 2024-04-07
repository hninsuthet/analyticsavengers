import pandas as pd
from create_rfmt_clv_tiers_df import get_clv_tiers
from create_df_auto import get_clv_df

# Automation for metrics
def generate_metrics_auto(df):

    # get clv df
    df_rfmt = get_clv_tiers(df)
    
    # Total Revenue = monetary_value.sum()
    total_revenue = df_rfmt['monetary_value'].sum()

    # Total customers = CustomerID.nunique()
    total_customers = df_rfmt['CustomerID'].nunique()

    # Average Customer Lifespan, in days
    # step 1: get extracted df of original df
    extracted_df = get_clv_df(df)

    # step 2: get lifespan for each customer
    extracted_df = extracted_df.groupby('CustomerID').agg(Lifespan=('InvoiceDate', lambda x: (x.max() - x.min()).days)).reset_index()

    # step 3: merge the extracted df with rfmt df
    merged_df = pd.merge(df_rfmt, extracted_df[['CustomerID', 'Lifespan']], on='CustomerID', how='inner')

    # step 4: calculate average customer lifespan in days
    average_customer_lifespan = merged_df['Lifespan'].mean()

    # Average Customer Lifetime Value = clv.mean()
    clv = df_rfmt['CLV'].mean()

    # create dataframe with the metrics
    metrics_data = pd.DataFrame({
        'Total Revenue': [total_revenue],
        'Total Customers': [total_customers],
        'Average Customer Lifespan': [average_customer_lifespan],
        'Average Customer Lifetime Value': [clv]
        
    })

    return metrics_data