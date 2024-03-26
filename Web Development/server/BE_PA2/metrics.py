import pandas as pd
import numpy as np 
import datetime as dt

# BG/NBD and Gamma-Gamma model from lifetimes package
from sklearn.cluster import KMeans
from sklearn.metrics import mean_squared_error
from lifetimes import BetaGeoFitter
from lifetimes import GammaGammaFitter
from lifetimes.utils import calibration_and_holdout_data
from lifetimes.utils import summary_data_from_transaction_data
from lifetimes.plotting import plot_calibration_purchases_vs_holdout_purchases

from create_df_statsclvrfm import get_clv_df

# Automation for metrics
def generate_metrics_auto(df):

    # get clv df
    df = get_clv_df(df)
    print(df.info())
    # STEP 1: Data Preprocessing - RFM Analysis and Data Splitting
    df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]

    # Computing the summary data (Recency, Frequency, monetary and tenure), grouped by CustomerID
    df['Monetary'] = df['UnitPrice'] * df['Quantity']
    df_rfmt = summary_data_from_transaction_data(transactions = df, 
                                            customer_id_col = 'CustomerID', 
                                            datetime_col = 'InvoiceDate', 
                                            monetary_value_col = 'Monetary')
    
    # get time period of entire dataset
    # print(df.info())
    diff_time = df['InvoiceDate'].max() - df['InvoiceDate'].min()
    diff_in_days = diff_time.days

    # get the calibration period for training set - 2/3 of entire period
    callibration_period = 2/3 * diff_in_days

    # Getting the ending date of the calibration period. 
    end_date_cal = df['InvoiceDate'].min() + dt.timedelta(days=callibration_period) 
    end_date_obs = end_date_cal + (diff_time - dt.timedelta(days=callibration_period))

    # Splitting the dataset into calibration and holdout data
    df_rfmt_cal = calibration_and_holdout_data(transactions=df, 
                                          customer_id_col="CustomerID",
                                          datetime_col = "InvoiceDate", 
                                          calibration_period_end=end_date_cal,
                                          observation_period_end= end_date_obs)
    
    # STEP 2: L2 regularisation - Finding best L2 coefficient using Grid Search
    l2_coefs = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
    l2_list = []
    rmse_list = []
    for coef in l2_coefs :
        # Fitting the model using the calibration dataset.
        model = BetaGeoFitter(penalizer_coef=coef)
        model.fit(df_rfmt_cal['frequency_cal'], 
            df_rfmt_cal['recency_cal'], 
            df_rfmt_cal['T_cal'])
        # Predicting the frequency for the holdout period for all customers. 
        pred_freq = pd.DataFrame(model.predict(df_rfmt_cal['duration_holdout'], 
                                    df_rfmt_cal['frequency_cal'], df_rfmt_cal['recency_cal'], df_rfmt_cal['T_cal']), columns=['pred_frequency']).reset_index()
        # Merging the two dataframes and dropping NaN values. 
        new_df = df_rfmt_cal.reset_index().merge(pred_freq, on='CustomerID').dropna()

        # Computing the rmse score 
        rmse_score = np.sqrt(mean_squared_error(new_df['frequency_holdout'],new_df['pred_frequency']))
        l2_list.append(coef)
        rmse_list.append(rmse_score)

    # Getting the results 
    resl = pd.DataFrame(np.array(rmse_list), columns=['rmse_score'])\
             .merge(pd.DataFrame(np.array(l2_list), columns=['L2 coefs']), right_index=True, left_index=True)
    
    # Getting the best L2 coefficient
    best_l2_coef = resl.loc[resl['rmse_score'].idxmin(), 'L2 coefs']

    # STEP 3: Fitting the BG/NBD model using the calibration dataset.
    model = BetaGeoFitter(penalizer_coef=best_l2_coef)
    model.fit(df_rfmt_cal['frequency_cal'], 
            df_rfmt_cal['recency_cal'], 
            df_rfmt_cal['T_cal'])
    
    # STEP 4: Predicting the number of purchases in the next 6 months (180 days) for all customers.
    df_rfmt['predicted_purchases'] = model.conditional_expected_number_of_purchases_up_to_time(180, 
                                                                                        df_rfmt['frequency'], 
                                                                                        df_rfmt['recency'], 
                                                                                        df_rfmt['T'])
    # Getting rid of NaN values and negative values.
    df_rfmt.dropna(inplace=True)
    df_rfmt = df_rfmt[df_rfmt['monetary_value']>0]

    # STEP 5: Fitting the Gamma-Gamma model 
    gg_model = GammaGammaFitter()
    gg_model.fit(df_rfmt['frequency'], df_rfmt['monetary_value'])

    df_rfmt['pred_monetary'] = gg_model.conditional_expected_average_profit(
            df_rfmt['frequency'],
            df_rfmt['monetary_value'])
    
    # STEP 6: Predicting the CLV for the next 6 months (180 days) for all customers.
    df_rfmt['CLV'] = gg_model.customer_lifetime_value(
        model,
        df_rfmt['frequency'],
        df_rfmt['recency'],
        df_rfmt['T'],
        df_rfmt['monetary_value'],
        time = 6, # In months 
        )
    
    # STEP 7: Assigning the customers to different tiers based on their CLV
    # Sort the DataFrame by CLV in descending order
    df_rfmt = df_rfmt.sort_values(by='CLV', ascending=False)

    # Calculate the number of customers for each tier
    total_customers = len(df_rfmt)
    high_value_count = int(total_customers * 0.2)
    low_value_count = int(total_customers * 0.2)
    # medium_value_count = total_customers - high_value_count - low_value_count

    # Assign tiers based on CLV
    df_rfmt['Tier'] = 'Medium Tier CLV'  # Initialize all as medium value

    # Assign high value tier
    df_rfmt.iloc[:high_value_count, df_rfmt.columns.get_loc('Tier')] = 'High Tier CLV'

    # Assign low value tier
    df_rfmt.iloc[-low_value_count:, df_rfmt.columns.get_loc('Tier')] = 'Low Tier CLV'

    # Reset index "CustomerID" and move it to column,
    df_rfmt.reset_index(inplace=True)

    # Total Revenue = monetary_value.sum()
    total_revenue = df_rfmt['monetary_value'].sum()

    # Total customers = CustomerID.nunique()
    total_customers = df_rfmt['CustomerID'].nunique()

    # Average Customer Lifespan = T.mean(), in month
    average_customer_lifespan = int(df_rfmt['T'].mean()/30)

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