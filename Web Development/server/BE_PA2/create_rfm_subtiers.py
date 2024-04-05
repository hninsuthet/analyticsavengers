import pandas as pd 
import numpy as np
import datetime as dt
import math

from create_rfmt_clv_tiers_df import get_clv_tiers
import pandas as pd

def calculate_sub_tiers(df):

    rfm_df = get_clv_tiers(df)
    
    # Create new df for RFM calculation
    df_rfm = rfm_df[['CustomerID', 'recency', 'frequency', 'monetary_value', 'Tier']].copy()

    # Normalize the R, F, and M columns
    df_rfm['R_norm'] = (df_rfm['recency'] - df_rfm['recency'].min()) / (df_rfm['recency'].max() - df_rfm['recency'].min())
    df_rfm['F_norm'] = (df_rfm['frequency'] - df_rfm['frequency'].min()) / (df_rfm['frequency'].max() - df_rfm['frequency'].min())
    df_rfm['M_norm'] = (df_rfm['monetary_value'] - df_rfm['monetary_value'].min()) / (df_rfm['monetary_value'].max() - df_rfm['monetary_value'].min())

    # Calculate thresholds
    high_threshold = 0.7  # Represents the top 30 percentile
    low_threshold = 0.3  # Represents the bottom 30 percentile
    # Middle percentile range is implicitly from 0.3 to 0.7

    def calculate_percentile(column, high_threshold, low_threshold):
        """
        Calculate high, middle, and low thresholds for a given RFM component
        """
        high_val = column.quantile(high_threshold)
        low_val = column.quantile(low_threshold)
        return high_val, low_val

    # Calculate thresholds for R, F, M components
    r_high, r_low = calculate_percentile(df_rfm['R_norm'], high_threshold, low_threshold)
    f_high, f_low = calculate_percentile(df_rfm['F_norm'], high_threshold, low_threshold)
    m_high, m_low = calculate_percentile(df_rfm['M_norm'], high_threshold, low_threshold)


    def assign_subtier(row):
        r, f, m = row['R_norm'], row['F_norm'], row['M_norm']
        tier = row['Tier']

        if tier == 'High Tier CLV':
            if f >= f_high and m >= m_high and r >= r_high:
                return 'High-Value'
            elif f >= f_high and m != m_high and r != r_high:
                return 'Loyal'
            #elif r >= r_high and f <= f_low:
                #return 'New'
            elif f <= f_low and m >= m_high and r != r_high:
                return 'At-Risk'
        elif tier == 'Middle Tier CLV':
            if f != f_low or m >= m_high:  # Assuming "higher" for Middle CLV tier
                return 'Potential Spenders'
            else:
                return 'Casual Spenders'
        elif tier == 'Low Tier CLV':
            if f != f_low or m >= m_high:  # Assuming "higher" for Low CLV tier
                return 'Least Engaged'
            else:
                return 'Asleep'
        return 'Unassigned'

    # Apply the subtier assignment function
    df_subtiers = df_rfm.copy()
    df_subtiers['Sub_Tier'] = df_subtiers.apply(assign_subtier, axis=1)
    df_subtiers = df_subtiers.drop(columns=['recency', 'frequency', 'monetary_value', 'R_norm', 'F_norm', 'M_norm'])
    
    return df_subtiers
