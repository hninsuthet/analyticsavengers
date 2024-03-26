import pandas as pd
from fuzzywuzzy import fuzz

import math
import ast

from create_rfm_subtiers import calculate_sub_tiers

def create_customer_profiling(df):

    # original df
    df = df.copy()
    # rfm df
    df_rfm = calculate_sub_tiers(df)

    df_subtier_unique = df_rfm.merge(df, how='left', on='CustomerID').drop_duplicates(subset='CustomerID', keep="first").drop(columns=['InvoiceNo', 'StockCode'])
    df_final = pd.DataFrame(df_subtier_unique.Sub_Tier.unique(), columns = ["Sub_Tier"])

    # adding gender distribution to df
    for index, x in enumerate(df_subtier_unique.Sub_Tier.unique()):
        df_tier = df_subtier_unique[df_subtier_unique['Sub_Tier'] == x]
        df_final.loc[index, "Female_Proportion"] = round((df_tier['Gender'].value_counts()['F']/df_tier.shape[0])*100)
        df_final.loc[index, "Male_Proportion"] = round((df_tier['Gender'].value_counts()['M']/df_tier.shape[0])*100)

    # adding country distribution to df
    for index, x in enumerate(df_subtier_unique.Sub_Tier.unique()):
        country_dict = {}
        df_tier = df_subtier_unique[df_subtier_unique['Sub_Tier'] == x]
        for val, cnt in df_tier["Country"].value_counts(normalize=True).items(): 
            country_dict[val] = round(cnt,2)
        df_final.loc[index, "Proportion_of_Countries"] = str(country_dict)

    for index, x in enumerate(df_final["Proportion_of_Countries"]):
        df_final["Proportion_of_Countries"][index] = ast.literal_eval(x)

    df_subtier = df_rfm.merge(df, how='left', on='CustomerID').drop(columns=['InvoiceNo', 'StockCode'])
    df_subtier["OrderValue"] = df_subtier["Quantity"] * df_subtier["UnitPrice"]
    df_subtier["OrderCount"] = 1

    # adding best selling categories to df
    for index, x in enumerate(df_subtier.Sub_Tier.unique()):
        category_dict = {}
        df_tier = df_subtier[df_subtier['Sub_Tier'] == x]
        category_df = df_tier.groupby("Category").sum(numeric_only=True, min_count=0).nlargest(5, 'Quantity').drop(columns=['CustomerID', 'recency', 'frequency', 'monetary_value', 'RFM_Score', 'UnitPrice', 'OrderValue', 'OrderCount'])
        category_df.reset_index(level=0, inplace=True)
        for i in range (0, len(category_df)):
            category_dict[category_df["Category"][i]] = category_df["Quantity"][i]
        df_final.loc[index, "Best_Selling_Categories"] = str(category_dict)

    for index, x in enumerate(df_final["Best_Selling_Categories"]):
        df_final["Best_Selling_Categories"][index] = ast.literal_eval(x)

    # adding best selling products to df
    for index, x in enumerate(df_subtier.Sub_Tier.unique()):
        description_dict = {}
        df_tier = df_subtier[df_subtier['Sub_Tier'] == x]
        description_df = df_tier.groupby("Description").sum(numeric_only=True, min_count=0).nlargest(5, 'Quantity').drop(columns=['CustomerID', 'recency', 'frequency', 'monetary_value', 'RFM_Score', 'UnitPrice', 'OrderValue', 'OrderCount'])
        description_df.reset_index(level=0, inplace=True)
        for i in range (0, len(description_df)):
            description_dict[description_df["Description"][i]] = description_df["Quantity"][i]
        df_final.loc[index, "Best_Selling_Products"] = str(description_dict)

    for index, x in enumerate(df_final["Best_Selling_Products"]):
        df_final["Best_Selling_Products"][index] = ast.literal_eval(x)

    # adding avg order amount & avg order size to df
    # Initialize empty lists to store calculated values
    avg_order_amount_list = []
    avg_order_size_list = []

    # Iterate over unique values in 'Sub_Tier' column
    for x in df_subtier['Sub_Tier'].unique():
        # Filter DataFrame for the current 'Sub_Tier' value
        subset = df_subtier[df_subtier['Sub_Tier'] == x]
        
        # Calculate sum of OrderValue, OrderCount, and Quantity
        ordervalue = subset['OrderValue'].sum()
        ordercount = subset['OrderCount'].sum()
        qty = subset['Quantity'].sum()
        
        # Calculate average order amount and size, handling division by zero
        if ordercount != 0:
            avg_order_amount = round(ordervalue / ordercount, 2)
            avg_order_size = math.floor(qty / ordercount)
        else:
            avg_order_amount = 0
            avg_order_size = 0
        
        # Append calculated values to the respective lists
        avg_order_amount_list.append(avg_order_amount)
        avg_order_size_list.append(avg_order_size)

    # Assign calculated values to new columns in df_final
    df_final['AVG_Order_Amount'] = avg_order_amount_list
    df_final['AVG_Order_Size'] = avg_order_size_list
            
    return df_final




