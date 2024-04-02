import pandas as pd
from fuzzywuzzy import fuzz

import math
import ast

from create_df_auto import get_profiling_df
from create_rfm_subtiers import calculate_sub_tiers

def create_customer_profiling(df):

    # get profiling df - df2
    # columns retrieved: CustomerID, Description, UnitPrice, Quantity, Country, Gender, Category
    profiling_df = get_profiling_df(df)

    # get rfm subtiers df - df
    # columns retrieved: CustomerID, Tier, Sub_Tier
    df_rfm = calculate_sub_tiers(df)

    # TEST
    df_subtier_unique = df_rfm.merge(profiling_df, how='left', on='CustomerID').drop_duplicates(subset='CustomerID', keep="first")

    # Group by 'Sub_Tier' and aggregate 'Tier' values
    df_final = df_rfm.groupby('Sub_Tier')['Tier'].unique().reset_index()
    df_final['Tier'] = df_final['Tier'].apply(lambda x: ', '.join(x))

    # Add 'Num_Customers' column
    df_final['Num_Customers'] = df_rfm.groupby('Sub_Tier')['CustomerID'].nunique().reset_index(drop=True)

    # Rearranging columns
    df_final = df_final[['Tier', 'Sub_Tier', 'Num_Customers']]
    
    for x in df_subtier_unique.Sub_Tier.unique():
        df_tier = df_subtier_unique[df_subtier_unique['Sub_Tier'] == x]
        # print("Top country of " + str(x) + " sub tier: " + str(df_tier['Country'].mode()[0]))
        # print("Gender distribution of " + str(x) + " sub tier: F - " + str(round((df_tier['Gender'].value_counts()['F']/df_tier.shape[0])*100)) + "% M - " + str(round((df_tier['Gender'].value_counts()['M']/df_tier.shape[0])*100)) + "% \n")

    for index, x in enumerate(df_subtier_unique.Sub_Tier.unique()):
        df_tier = df_subtier_unique[df_subtier_unique['Sub_Tier'] == x]
        df_final.loc[index, "Female_Proportion"] = round((df_tier['Gender'].value_counts()['F']/df_tier.shape[0])*100)
        df_final.loc[index, "Male_Proportion"] = round((df_tier['Gender'].value_counts()['M']/df_tier.shape[0])*100)

    for index, x in enumerate(df_subtier_unique.Sub_Tier.unique()):
        country_dict = {}
        df_tier = df_subtier_unique[df_subtier_unique['Sub_Tier'] == x]
        for val, cnt in df_tier["Country"].value_counts(normalize=True).items(): 
            country_dict[val] = round(cnt,2)
        df_final.loc[index, "Proportion_of_Countries"] = str(country_dict)

    df_subtier = df_rfm.merge(profiling_df, how='left', on='CustomerID')
    df_subtier["OrderValue"] = df_subtier["Quantity"] * df_subtier["UnitPrice"]
    df_subtier["OrderCount"] = 1

    for x in df_subtier.Sub_Tier.unique():
        # print("\033[1m" + str(x) + " sub tier best selling categories" + "\033[0;0m")
        df_tier = df_subtier[df_subtier['Sub_Tier'] == x]
        # print(df_tier.groupby("Category").sum(numeric_only=True, min_count=0).nlargest(5, 'Quantity').drop(columns=['CustomerID', 'UnitPrice', 'OrderValue', 'OrderCount']))
        # print("\n")

    for index, x in enumerate(df_subtier.Sub_Tier.unique()):
        category_dict = {}
        df_tier = df_subtier[df_subtier['Sub_Tier'] == x]
        category_df = df_tier.groupby("Category").sum(numeric_only=True, min_count=0).nlargest(5, 'Quantity').drop(columns=['CustomerID', 'UnitPrice', 'OrderValue', 'OrderCount'])
        category_df.reset_index(level=0, inplace=True)
        for i in range (0, len(category_df)):
            category_dict[category_df["Category"][i]] = category_df["Quantity"][i]
        df_final.loc[index, "Best_Selling_Categories"] = str(category_dict)

    for x in df_subtier.Sub_Tier.unique():
        # print("\033[1m" + str(x) + " sub tier best selling products" + "\033[0;0m")
        df_tier = df_subtier[df_subtier['Sub_Tier'] == x]
        # print(df_tier.groupby("Description").sum(numeric_only=True, min_count=0).nlargest(5, 'Quantity').drop(columns=['CustomerID', 'UnitPrice', 'OrderValue', 'OrderCount']))
        # print("\n")

    for index, x in enumerate(df_subtier.Sub_Tier.unique()):
        description_dict = {}
        df_tier = df_subtier[df_subtier['Sub_Tier'] == x]
        description_df = df_tier.groupby("Description").sum(numeric_only=True, min_count=0).nlargest(5, 'Quantity').drop(columns=['CustomerID', 'UnitPrice', 'OrderValue', 'OrderCount'])
        description_df.reset_index(level=0, inplace=True)
        for i in range (0, len(description_df)):
            description_dict[description_df["Description"][i]] = description_df["Quantity"][i]
        df_final.loc[index, "Best_Selling_Products"] = str(description_dict)

    for x in df_subtier.Sub_Tier.unique():
        ordervalue = df_subtier[df_subtier['Sub_Tier'] == x].sum(numeric_only=True, min_count=0)["OrderValue"]
        ordercount = df_subtier[df_subtier['Sub_Tier'] == x].sum(numeric_only=True, min_count=0)["OrderCount"]
        qty = df_subtier[df_subtier['Sub_Tier'] == x].sum(numeric_only=True, min_count=0)["Quantity"]
        # print(str(x) + " sub tier AVG order amount: $" + str(round((ordervalue/ordercount), 2)))
        # print(str(x) + " sub tier AVG order size: " + str(math.floor(qty/ordercount)) + "\n")

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




