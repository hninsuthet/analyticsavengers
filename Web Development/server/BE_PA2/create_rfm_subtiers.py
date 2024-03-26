import pandas as pd 
import numpy as np
import datetime as dt
import math

# BG/NBD and Gamma-Gamma model from lifetimes package
from sklearn.cluster import KMeans
from sklearn.metrics import mean_squared_error
from lifetimes import BetaGeoFitter
from lifetimes import GammaGammaFitter
from lifetimes.utils import calibration_and_holdout_data
from lifetimes.utils import summary_data_from_transaction_data

from create_clv_tiers_df import get_clv_tiers
import pandas as pd

def calculate_sub_tiers(df):

    rfm_df = get_clv_tiers(df)
    
    # Create new df for RFM calculation
    df_rfm = rfm_df[['CustomerID', 'recency', 'frequency', 'monetary_value', 'Tier']].copy()

    # Normalize the R, F, and M columns
    df_rfm['R_norm'] = (df_rfm['recency'] - df_rfm['recency'].min()) / (df_rfm['recency'].max() - df_rfm['recency'].min())
    df_rfm['F_norm'] = (df_rfm['frequency'] - df_rfm['frequency'].min()) / (df_rfm['frequency'].max() - df_rfm['frequency'].min())
    df_rfm['M_norm'] = (df_rfm['monetary_value'] - df_rfm['monetary_value'].min()) / (df_rfm['monetary_value'].max() - df_rfm['monetary_value'].min())

    # Calculate weighted RFM score
    df_rfm['RFM_Score'] = 1 * df_rfm['R_norm'] + 3 * df_rfm['F_norm'] + 3 * df_rfm['M_norm']

    # Drop the normalized columns
    df_rfm = df_rfm.drop(['R_norm', 'F_norm', 'M_norm'], axis=1)

    # Calculate the quantiles within each CLV tier group.
    quantiles = df_rfm.groupby('Tier')['RFM_Score'].quantile([0.4, 0.6, 0.8]).unstack()

    def assign_tier(row):
        clv_tier = row['Tier']
        rfm_score = row['RFM_Score']
        # High CLV Tier
        if clv_tier == 'High Tier CLV':
            if rfm_score <= quantiles.loc[clv_tier, 0.4]:
                return 'Silver'
            elif rfm_score <= quantiles.loc[clv_tier, 0.8]:
                return 'Gold'
            else:
                return 'Platinum'
        # Medium CLV Tier
        elif clv_tier == 'Medium Tier CLV':
            if rfm_score <= quantiles.loc[clv_tier, 0.6]:
                return 'Copper'
            else:
                return 'Bronze'
        # Low CLV Tier
        elif clv_tier == 'Low Tier CLV':
            if rfm_score <= quantiles.loc[clv_tier, 0.6]:
                return 'Lead'
            else:
                return 'Iron'
        # Default case if none above
        return 'Unassigned'

    # Create new df for RFM tiering
    df_subtiers = df_rfm[['CustomerID', 'recency', 'frequency', 'monetary_value', 'RFM_Score', 'Tier']].copy()

    # Apply the function to each row to assign the tier
    df_subtiers['Sub_Tier'] = df_subtiers.apply(assign_tier, axis=1)
    
    return df_subtiers

