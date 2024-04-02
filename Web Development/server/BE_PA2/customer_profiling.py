import pandas as pd
from fuzzywuzzy import fuzz

import math
import ast

from create_df_auto import get_profiling_df
from create_rfm_subtiers import calculate_sub_tiers

def create_customer_profiling(df):

    # get profiling df
    # columns retrieved: CustomerID, Description, UnitPrice, Quantity, Country, Gender, Category
    df = get_profiling_df(df)

    # get rfm subtiers df
    # columns retrieved: CustomerID, Tier, Sub_Tier
    df_rfm = calculate_sub_tiers(df)

    # create final df 
    # columns created: Tier, Sub_Tier, Num_Customers
    df_final = df.groupby('Sub_Tier')['Tier'].unique().reset_index()
    df_final['Tier'] = df_final['Tier'].apply(lambda x: ', '.join(x))
    df_final['Num_Customers'] = df.groupby('Sub_Tier')['CustomerID'].nunique().reset_index(drop=True)
    df_final = df_final[['Tier', 'Sub_Tier', 'Num_Customers']]

    # create df_subtier_unique (keep only the first transaction of each customer) 
    df_subtier_unique = df_rfm.merge(df, how='left', on='CustomerID').drop_duplicates(subset='CustomerID', keep="first")

    # adding gender distribution column to df_final
    for index, x in enumerate(df_subtier_unique.Sub_Tier.unique()):
        df_tier = df_subtier_unique[df_subtier_unique['Sub_Tier'] == x]
        df_final.loc[index, "Female_Proportion"] = round((df_tier['Gender'].value_counts()['F']/df_tier.shape[0])*100)
        df_final.loc[index, "Male_Proportion"] = round((df_tier['Gender'].value_counts()['M']/df_tier.shape[0])*100)

    # adding country distribution column to df_final
    for index, x in enumerate(df_subtier_unique.Sub_Tier.unique()):
        country_dict = {}
        df_tier = df_subtier_unique[df_subtier_unique['Sub_Tier'] == x]
        for val, cnt in df_tier["Country"].value_counts(normalize=True).items(): 
            country_dict[val] = round(cnt,2)
        df_final.loc[index, "Proportion_of_Countries"] = str(country_dict)

    # create df_subtier (retains all transactions from each customer)
    df_subtier = df_rfm.merge(df, how='left', on='CustomerID').drop(columns=['InvoiceNo', 'StockCode'])
    df_subtier["OrderValue"] = df_subtier["Quantity"] * df_subtier["UnitPrice"]
    df_subtier["OrderCount"] = 1

    # adding best selling categories column to df_final
    for index, x in enumerate(df_subtier.Sub_Tier.unique()):
        category_dict = {}
        df_tier = df_subtier[df_subtier['Sub_Tier'] == x]
        category_df = df_tier.groupby("Category").sum(numeric_only=True, min_count=0).nlargest(5, 'Quantity').drop(columns=['CustomerID', 'recency', 'frequency', 'monetary_value', 'UnitPrice', 'OrderValue', 'OrderCount'])
        category_df.reset_index(level=0, inplace=True)
        for i in range (0, len(category_df)):
            category_dict[category_df["Category"][i]] = category_df["Quantity"][i]
        df_final.loc[index, "Best_Selling_Categories"] = str(category_dict)

    # adding best selling products column to df_final
    for index, x in enumerate(df_subtier.Sub_Tier.unique()):
        description_dict = {}
        df_tier = df_subtier[df_subtier['Sub_Tier'] == x]
        description_df = df_tier.groupby("Description").sum(numeric_only=True, min_count=0).nlargest(5, 'Quantity').drop(columns=['CustomerID', 'recency', 'frequency', 'monetary_value', 'UnitPrice', 'OrderValue', 'OrderCount'])
        description_df.reset_index(level=0, inplace=True)
        for i in range (0, len(description_df)):
            description_dict[description_df["Description"][i]] = description_df["Quantity"][i]
        df_final.loc[index, "Best_Selling_Products"] = str(description_dict)

    # adding avg order amount & avg order size columns to df_final
    for index, x in enumerate(df_subtier.Sub_Tier.unique()):
        ordervalue = df_subtier[df_subtier['Sub_Tier'] == x].sum(numeric_only=True, min_count=0)["OrderValue"]
        ordercount = df_subtier[df_subtier['Sub_Tier'] == x].sum(numeric_only=True, min_count=0)["OrderCount"]
        qty = df_subtier[df_subtier['Sub_Tier'] == x].sum(numeric_only=True, min_count=0)["Quantity"]
        
        avg_order_amount = round((ordervalue / ordercount), 2)
        avg_order_size = math.floor(qty / ordercount)
        
        # Assign the calculated average values for each Sub_Tier
        df_final.at[index, "AVG_Order_Amount"] = avg_order_amount
        df_final.at[index, "AVG_Order_Size"] = avg_order_size
            
    return df_final




