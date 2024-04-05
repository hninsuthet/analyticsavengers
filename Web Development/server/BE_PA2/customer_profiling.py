import pandas as pd
import math
import ast

from create_df_auto import get_profiling_df
from create_rfm_subtiers import calculate_sub_tiers

def create_customer_profiling(df):

    # get profiling df
    # columns retrieved: CustomerID, Description, UnitPrice, Quantity, Country, Gender, Category
    profiling_df = get_profiling_df(df)

    # get rfm subtiers df
    # columns retrieved: CustomerID, Tier, Sub_Tier
    df_rfm = calculate_sub_tiers(df)

    # create final df 
    # columns created: Tier, Sub_Tier, Subtier_Description, Num_Customers
    df_final = df_rfm.groupby('Sub_Tier')['Tier'].unique().reset_index()
    df_final['Tier'] = df_final['Tier'].apply(lambda x: ', '.join(x))
    df_final['Num_Customers'] = df_rfm.groupby('Sub_Tier')['CustomerID'].nunique().reset_index(drop=True)
    subtier_description = {
        'High-Value': 'High-Value customers are your top-tier patrons, showcasing high engagement across recent purchases, frequency, and monetary value. They consistently contribute significantly to your revenue, demonstrating both loyalty and high spending capacity.',
        'Loyal': 'Loyal customers exhibit strong purchase frequency, indicating a deep connection with your brand, though they might not always spend the most or shop the most recently. Their repeated business signifies trust and habituation with your offerings.',
        'At-Risk': 'At-Risk customers used to spend significantly but have shown a decrease in purchase frequency and recent engagement. They are at a critical juncture, requiring immediate re-engagement strategies to prevent churn.',
        'Potential Spenders': 'Potential Spenders are customers with varying engagement levels who have shown some signs of high spending or frequent purchases. They hold the promise of moving up to higher-value tiers with the right incentives and engagement.',
        'Casual Spenders': 'Casual Spenders engage with your brand sporadically, with neither low nor high frequency or spending. They represent an opportunity for increased engagement through targeted marketing efforts.',
        'Least Engaged': 'Least Engaged customers have interacted with your brand but show low levels of frequency and spending. Identifying barriers to their engagement and addressing these can help in moving them to more active segments.',
        'Asleep': 'Asleep customers have the lowest levels of engagement, with minimal recent interaction or spending. Reawakening their interest in your brand requires innovative re-engagement and personalized marketing strategies.'
    }
    df_final['Subtier_Description'] = df_final['Sub_Tier'].map(subtier_description) # Map sub-tier descriptions to sub-tiers in the DataFrame
    df_final = df_final[['Tier', 'Sub_Tier', 'Subtier_Description','Num_Customers']] # Reorder columns

    # create df_subtier_unique (keep only the first transaction of each customer) 
    # columns created: CustomerID, Tier, Sub_Tier Description, UnitPrice, Quantity, Country, Gender, Category
    df_subtier_unique = df_rfm.merge(profiling_df, how='left', on='CustomerID').drop_duplicates(subset='CustomerID', keep="first")

    # adding gender distribution column to df_final
    for index, x in enumerate(df_subtier_unique.Sub_Tier.unique()):
        df_tier = df_subtier_unique[df_subtier_unique['Sub_Tier'] == x]
        df_final.loc[index, "Female_Proportion"] = round((df_tier['Gender'].value_counts()['F']/df_tier.shape[0])*100)
        df_final.loc[index, "Male_Proportion"] = round((df_tier['Gender'].value_counts()['M']/df_tier.shape[0])*100)

    # adding country distribution column to df_final
    for index, x in enumerate(df_subtier_unique.Sub_Tier.unique()):
        country_dict = {}
        df_tier = df_subtier_unique[df_subtier_unique['Sub_Tier'] == x]
        for val, cnt in df_tier["Country"].value_counts().items(): 
            country_dict[val] = round(cnt,2)
        df_final.loc[index, "Country_Distribution"] = str(country_dict)

    # create df_subtier (retains all transactions from each customer)
    df_subtier = df_rfm.merge(df, how='left', on='CustomerID')
    df_subtier["OrderValue"] = df_subtier["Quantity"] * df_subtier["UnitPrice"]
    df_subtier["OrderCount"] = 1

    # adding best selling categories column to df_final
    for index, x in enumerate(df_subtier.Sub_Tier.unique()):
        category_dict = {}
        df_tier = df_subtier[df_subtier['Sub_Tier'] == x]
        category_df = df_tier.groupby("Category").sum(numeric_only=True, min_count=0).nlargest(5, 'Quantity').drop(columns=['CustomerID', 'UnitPrice', 'OrderValue', 'OrderCount'])
        category_df.reset_index(level=0, inplace=True)
        for i in range (0, len(category_df)):
            category_dict[category_df["Category"][i]] = category_df["Quantity"][i]
        df_final.loc[index, "Best_Selling_Categories"] = str(category_dict)

    # adding best selling products column to df_final
    for index, x in enumerate(df_subtier.Sub_Tier.unique()):
        description_dict = {}
        df_tier = df_subtier[df_subtier['Sub_Tier'] == x]
        description_df = df_tier.groupby("Description").sum(numeric_only=True, min_count=0).nlargest(5, 'Quantity').drop(columns=['CustomerID', 'UnitPrice', 'OrderValue', 'OrderCount'])
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

    # Remove rows where Sub_Tier == "Unassigned"
    df_final = df_final[df_final['Sub_Tier'] != 'Unassigned'] 

    # Define custom sorting order for 'Sub_Tier' column
    subtier_order = ["High-Value", "Loyal", "At-Risk", "Potential Spenders", "Casual Spenders", "Least Engaged", "Asleep"]
    subtier_dtype = pd.CategoricalDtype(categories=subtier_order, ordered=True)
    
    # Convert 'Sub_Tier' column to categorical with custom order
    df_final['Sub_Tier'] = df_final['Sub_Tier'].astype(subtier_dtype)
    
    # Sort df_final by 'Sub_Tier' column
    df_final = df_final.sort_values(by='Sub_Tier')
            
    return df_final




