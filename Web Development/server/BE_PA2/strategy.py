import pandas as pd
import numpy as np

# For High Value Strategy: XGBoost & Random Forest
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from sklearn.ensemble import RandomForestClassifier
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

# For Loyal Customer Strategy:
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules
from mlxtend.preprocessing import TransactionEncoder

# Importing Functions
from create_df_auto import get_strategy_df, get_unique_products_df
from create_rfm_subtiers import calculate_sub_tiers

def get_data(df):
    # get strategy df
    # columns retrieved: CustomerID, InvoiceNo, StockCode, Description, InvoiceDate, UnitPrice, Quantity, Country, Gender, Category
    strategy_df = get_strategy_df(df)

    # get rfm subtiers df
    # columns retrieved: CustomerID, Tier, Sub_Tier
    df_rfm = calculate_sub_tiers(df)

    # merge df_rfm and strategy_df
    # columns created: CustomerID, Tier, Sub_Tier, InvoiceNo, StockCode, Description, InvoiceDate, UnitPrice, Quantity, Country, Gender, Category
    merged_df = df_rfm.merge(strategy_df, how='left', on='CustomerID')

    return merged_df

################################ High-Value Customer Strategy ################################
# Full High-Value Function
def generate_high_value_strategy(df):
    df_combined = get_data(df)

    # Get unique product list
    def process_product_list(df_combined):
        # Read the Excel file into a DataFrame
        df_productList = df_combined

        # Drop duplicates based on 'Description' while keeping the first occurrence
        unique_products_df = df_productList.drop_duplicates(subset=['Description'], keep='first')

        # Select only the 'Description', 'UnitPrice', and 'Category' columns
        unique_products_df = unique_products_df[['Description', 'UnitPrice', 'Category']]

        return unique_products_df
    unique_products_df = process_product_list(df_combined)

    # XGBOOST
    def xgb_create_features(df_combined):
        grouped = df_combined.groupby('CustomerID')

        # Ensure aggregation results in Series (adjusting the lambda functions as necessary)
        features_df = pd.DataFrame({
            'AveragePurchaseValue': grouped.apply(lambda x: (x['Quantity'] * x['UnitPrice']).mean()),
            'MaxPurchaseValue': grouped.apply(lambda x: (x['Quantity'] * x['UnitPrice']).max()),
            'TotalSpend': grouped.apply(lambda x: (x['Quantity'] * x['UnitPrice']).sum()),
            'PurchaseFrequency': grouped['InvoiceNo'].nunique(),
            'Recency': (pd.to_datetime('today') - pd.to_datetime(grouped['InvoiceDate'].max())).dt.days,
            'FavoriteCategory': grouped['Category'].apply(lambda x: x.mode()[0] if not x.mode().empty else np.nan),
            'NumberUniqueCategories': grouped['Category'].nunique(),
            'AverageUnitPrice': grouped['UnitPrice'].mean(),
            'MaxUnitPrice': grouped['UnitPrice'].max(),
            'DaysAsCustomer': (pd.to_datetime(grouped['InvoiceDate'].max()) - pd.to_datetime(grouped['InvoiceDate'].min())).dt.days,
            'NumberOfTransactions': grouped.size(),
        }).reset_index()

        # Merge with demographics (adjusting for potential multiple rows per CustomerID)
        demographics = df_combined[['CustomerID', 'Country', 'Gender']].drop_duplicates()
        features_df = features_df.merge(demographics, on='CustomerID', how='left')

        return features_df

    # XGBoost Features Data Frame
    xgb_features = xgb_create_features(df_combined)

    #XGBoost Model
    def train_xgboost (xgb_features):
        # Select features and target variable
        X = xgb_features.drop(['CustomerID', 'AverageUnitPrice'], axis=1)  # Remove non-feature and target columns
        y = xgb_features['AverageUnitPrice']  # Target variable

        # One-Hot Encoding for categorical variables
        categorical_vars = ['FavoriteCategory', 'Country', 'Gender']
        X = pd.get_dummies(X, columns=categorical_vars)

        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Initialize the XGBoost regressor
        xgb_model = XGBRegressor(objective='reg:squarederror', n_estimators=100)

        # Train the model
        xgb_model.fit(X_train, y_train)

        # Predict on the testing set
        predictions = xgb_model.predict(X_test)

        return xgb_model, X_train
    
    xgb_model, X_train = train_xgboost (xgb_features)


    def train_rf (df_combined):
        # Splitting features and target variables
        X2 = df_combined.drop(columns=['Category', 'CustomerID'])
        y2 = df_combined['Category']

        # Split your data
        X2_train, X2_test, y2_train, y2_test = train_test_split(X2, y2, test_size=0.2, random_state=42)

        # Identify categorical columns for one-hot encoding, excluding the target variable 'Category'
        categorical_features = ['Country', 'Gender']  # Specify categorical features here

        # Create ColumnTransformer to apply OneHotEncoder to categorical features
        preprocessor = ColumnTransformer(
            transformers=[
                ('cat', OneHotEncoder(drop='first'), categorical_features),  # One-hot encode categorical features
                
            ],
            remainder='drop'  # Change from 'passthrough' to 'drop' to avoid unexpected non-numeric data
        )

        # Create a pipeline with the preprocessor and a Random Forest Classifier
        rf_model = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('classifier', RandomForestClassifier())
        ])

        # Train the model
        rf_model.fit(X2_train, y2_train)

        predictions = rf_model.predict(X2_test)
        return rf_model
    
    rf_model = train_rf (df_combined)

    def suggest_product(customer_id, df_combined, xgb_model, rf_model, unique_products_df):
        def predict_next_purchase_unit_price(customer_id, df_combined, xgb_model):
            # Extract data for the specific customer
            customer_data = df_combined[df_combined['CustomerID'] == customer_id]
            
            # If customer data is empty, handle accordingly
            if customer_data.empty:
                print(f"No data found for CustomerID {customer_id}")
                return None
            
            # Apply feature engineering
            features_df = xgb_create_features(customer_data)
            
            # Ensure we're only using the features the model was trained on
            # Assume these are the features (excluding 'CustomerID' and target variable)
            features = features_df.drop(['CustomerID', 'AverageUnitPrice'], axis=1)
            
            # Apply one-hot encoding (as during model training)
            # Assuming 'categorical_vars' are your categorical variables from training
            categorical_vars = ['FavoriteCategory', 'Country', 'Gender']
            features_encoded = pd.get_dummies(features, columns=categorical_vars)
            
            # Ensure the features match the training data, including all necessary dummy columns
            train_features = X_train.columns  # Extracted from the training data above
            features_encoded = features_encoded.reindex(columns=train_features, fill_value=0)
            
            # Predict the unit price for the next purchase
            predicted_unit_price = xgb_model.predict(features_encoded)[0]
            
            return predicted_unit_price

        def predict_next_purchase_category(customer_id, df_combined, rf_model):
            # Extract data for the specific customer
            customer_data = df_combined[df_combined['CustomerID'] == customer_id]
            
            # If customer data is empty, handle accordingly
            if customer_data.empty:
                print(f"No data found for CustomerID {customer_id}")
                return None
            
            # Select features for prediction (excluding 'CustomerID' and 'Category')
            # Ensure that the features match those used during model training
            X_pred = customer_data.drop(columns=['Category', 'CustomerID'])
            
            # Apply one-hot encoding via the preprocessor in the pipeline
            # The pipeline will automatically handle one-hot encoding based on the setup during training
            predicted_category = rf_model.predict(X_pred)
            
            # Assuming we are predicting for a single instance and want a readable category
            predicted_category = predicted_category[0]
            
            return predicted_category

        predicted_category =  predict_next_purchase_category(customer_id, df_combined, rf_model) 
        predicted_unit_price_numeric = predict_next_purchase_unit_price(customer_id, df_combined, xgb_model)
        formatted_predicted_unit_price = f"${predicted_unit_price_numeric:.2f}"


        # Filter products by predicted category
        category_products = unique_products_df[unique_products_df['Category'] == predicted_category]
        
        # Further filter by unit price being higher than predicted unit price
        higher_price_products = category_products[category_products['UnitPrice'] > predicted_unit_price_numeric]
        
        if not higher_price_products.empty:
            # Find the product with unit price closest to the predicted unit price
            higher_price_products['PriceDifference'] = abs(higher_price_products['UnitPrice'] - predicted_unit_price_numeric)
            suggested_product = higher_price_products.sort_values(by='PriceDifference').iloc[0]
            
            
            return (suggested_product['Description'], suggested_product['UnitPrice'])
        else:
            # If no products match the criteria, return None or a default message
            return ("No suitable product found", None)
        
    def get_customers_by_sub_tier(df, sub_tier):
        filtered_df = df[df['Sub_Tier'] == sub_tier]
        unique_customers = filtered_df['CustomerID'].unique()
        unique_customers_df = pd.DataFrame(unique_customers, columns=['CustomerID'])
        return unique_customers_df
    
    def aggregate_product_suggestions(customers_df, df_combined, xgb_model, rf_model, unique_products_df):
        results = []
        for customer_id in customers_df['CustomerID']:
            suggested_product_description, suggested_product_price = suggest_product(customer_id, df_combined, xgb_model, rf_model, unique_products_df)
            results.append({
                'CustomerID': customer_id,
                'Suggested_Product_Description': suggested_product_description,
                'Suggested_Product_Price': suggested_product_price
            })
        results_df = pd.DataFrame(results)
        
        aggregation = results_df.groupby(['Suggested_Product_Description', 'Suggested_Product_Price']).agg(
            Number_of_Customers=('CustomerID', 'count'),
            List_of_CustomerID=('CustomerID', lambda x: list(x.unique()))  
        ).reset_index()
        
        sorted_aggregation = aggregation.sort_values(by='Number_of_Customers', ascending=False)
        
        return sorted_aggregation

    # Step 1: Get List of High-Value customerID
    sub_tier = "High-Value"
    HV_customers_df = get_customers_by_sub_tier(df_combined, sub_tier)
    
    # Step 2: Get final content
    aggregated_suggestions_df = aggregate_product_suggestions(HV_customers_df, df_combined, xgb_model, rf_model, unique_products_df)
    
    return aggregated_suggestions_df


################################ Loyal Customer Strategy ################################
# SUB-FUNCTION
def transactions_dataframe(df_combined):
    # First, filter the DataFrame for only 'Loyal' sub-tier customers
    df_combined = df_combined[df_combined['Sub_Tier'] == 'Loyal']

    # Calculate the sale amount for each item in the transaction
    df_combined['ItemSaleAmount'] = df_combined['Quantity'] * df_combined['UnitPrice']

    # Group by 'InvoiceNo' and aggregate data
    df_transactions = df_combined.groupby('InvoiceNo').agg({
        'StockCode': lambda x: list(x),
        'Description': lambda x: list(x),
        'CustomerID': 'first',
        'Country': 'first',
        'Gender': 'first',
        'Category': lambda x: list(x.unique()),
        'Tier': 'first',
        'Sub_Tier': 'first',
        'ItemSaleAmount': 'sum'  # Sum the sale amounts for items within the same transaction
    }).reset_index()

    # Rename 'ItemSaleAmount' to 'SaleAmount' for clarity
    df_transactions.rename(columns={'ItemSaleAmount': 'SaleAmount'}, inplace=True)

    return df_transactions

# SUB-FUNCTION
def generate_bundles(df_transactions):
    # Extracting 'Description' for Apriori algorithm
    transactions = df_transactions['Description'].tolist()
    
    # Instantiate the TransactionEncoder, fit and transform the data
    encoder = TransactionEncoder()
    encoded_array = encoder.fit(transactions).transform(transactions)
    
    # Convert the array of transactions into DataFrame
    df_encoded = pd.DataFrame(encoded_array, columns=encoder.columns_)

    # About minimum support, support = No. of transaction with the set/Total transactions
    # Lower for a big dataset, higher for a smaller dataset
    # min_support parameter determines the minimum support value for an itemset to be considered frequent
    min_support=0.01

    # Apply the Apriori algorithm to find frequent itemsets
    frequent_itemsets = apriori(df_encoded, min_support=min_support, use_colnames=True)

    # Explanation of control metrics
    # Confidence -  measures the likelihood of item B being purchased when item A is purchased. support(A ∪ B) / support(A).
    # Lift - The ratio of the observed support of A and B together to the expected support if A and B were independent. support(A ∪ B) / (support(A) * support(B)).
    
    # Define metrics and thresholds for filtering
    metric = "confidence"
    min_confidence = 0.1
    min_lift = 1.5

    # Generate association rules
    rules = association_rules(frequent_itemsets, metric = metric, min_threshold = min_confidence)
    
    # Filter rules based on the lift threshold
    filtered_rules = rules[rules['lift'] >= min_lift]

    
    return filtered_rules

# SUB-FUNCTION. ONLY ARM FUNCTION. 
def recommend_next_items(customer_id, df_combined, bundling_rules):
    # Extract customer's purchased items
    customer_items = df_combined[df_combined['CustomerID'] == customer_id]['Description'].unique()
    
    # Convert customer_items to a set for easier comparison
    customer_items_set = set(customer_items)
    
    # Prepare a list to store recommended items
    recommended_items = set()
    
    # Iterate through the bundling_rules
    for _, rule in bundling_rules.iterrows():
        antecedents = set(rule['antecedents'])
        
        # Check if customer's items match the rule's antecedents
        if antecedents.issubset(customer_items_set):
            # Add consequents to the recommended items if they're not already purchased
            consequents = set(rule['consequents'])
            new_recommendations = consequents - customer_items_set
            recommended_items.update(new_recommendations)
            
    # Convert the recommended items set to a sorted list (optional: based on preference)
    recommended_items_list = sorted(recommended_items)
    
    return recommended_items_list

# FINAL FUNCTION. Using only ARM Modelling and functions
def generate_loyal_strategy(df_combined, top_n=3):
    df_combined = get_data(df_combined)
    bundling_rules = generate_bundles(transactions_dataframe(df_combined))
    
    def get_customers_by_sub_tier(df):
        filtered_df = df[df['Sub_Tier'] == 'Loyal']
        unique_customers = filtered_df['CustomerID'].unique()
        return unique_customers
    
    # Retrieve unique CustomerIDs for the subtier
    customers = get_customers_by_sub_tier(df_combined)
    
    # Initialize an empty list to store recommendation results
    recommendations = []
    
    # Iterate over each customer and generate recommendations
    for customer_id in customers:
        try:
            top_recommendations = recommend_next_items(customer_id, df_combined, bundling_rules)
            top_recommendations = top_recommendations[:top_n]
            recommendations.append({
                'CustomerID': customer_id,
                'Top Recommendations': ', '.join(top_recommendations)  # Concatenate recommendations into a single string
            })
        except ValueError as e:
            print(f"Error processing CustomerID {customer_id}: {e}")
    
    # Convert the recommendations list to a DataFrame
    recommendations_df = pd.DataFrame(recommendations)
    return recommendations_df


################################ At-Risk Customer Strategy ################################
# SUB-FUNCTION: find the best-selling category for each at-risk customer
def identify_best_selling_category(df):
    # get combined dataframe
    # columns retrieved: CustomerID, Tier, Sub_Tier, InvoiceNo, StockCode, Description, InvoiceDate, UnitPrice, Quantity, Country, Gender, Category
    df = get_data(df)

    # Filter the dataframe to only include at-risk customers
    filtered = df[df['Sub_Tier'] == 'At-Risk']

    # Retrieve only the columns needed in df
    result_df = filtered[['CustomerID', 'Description', 'Category', 'InvoiceNo', 'Quantity']].copy()

    #calculate which category is the best selling category for each customerID based on quantity
    best_selling_category = result_df.groupby(['CustomerID', 'Category'])['Quantity'].sum().reset_index()

    #get the output to only show the best selling category for each customerID
    best_selling_category = best_selling_category.sort_values('Quantity', ascending=False).drop_duplicates(['CustomerID']).reset_index(drop=True)

    return best_selling_category

# FINAL FUNCTION: assign discount tiers to at-risk customers
def assign_discount_tiers(df):
    """
    Assign discount tiers to at-risk customers based on their purchase frequency in the best-selling category.
    Returns a DataFrame with the following columns: Category, DiscountTier, NumCustomers, CustomerIDs.
    - Category: The best-selling category for the at-risk customer.
    - DiscountTier: The assigned discount tier based on purchase frequency in the best-selling category.
    - NumCustomers: The number of at-risk customers in the category assigned to the discount tier.
    - CustomerIDs: A list of CustomerIDs for the at-risk customers in the category assigned to the discount tier.
    """
    # Define discount tiers (modify as needed)
    discount_tiers = {
        5: (1, 200, 5),  # Percentage discounts for tier 1 (2-3 purchases)
        10: (201, 500, 10),  # Percentage discounts for tier 2 (4-6 purchases)
        15: (501, None, 15)  # Percentage discounts for tier 3 (7 or more purchases)
    }

    # Find the best-selling category for each at-risk customer
    df_with_best_selling_category = identify_best_selling_category(df)

    # Group by customer and category, calculate purchase frequency
    df_grouped = df_with_best_selling_category.groupby(['CustomerID', 'Category'])['Quantity'].sum().reset_index()
    df_grouped.rename(columns={'Quantity': 'PurchaseFrequency'}, inplace=True)

    # Assign discount tier based on purchase frequency
    def assign_tier(frequency):
        for tier, (min_purchase, max_purchase, discount) in discount_tiers.items():
            if (min_purchase is None or frequency >= min_purchase) and (max_purchase is None or frequency <= max_purchase):
                return tier
        return None

    df_grouped['DiscountTier'] = df_grouped['PurchaseFrequency'].apply(assign_tier)
    df_grouped = df_grouped.groupby(['Category', 'DiscountTier']).agg(NumCustomers=('CustomerID', 'count'), CustomerIDs=('CustomerID', list)).reset_index()

    return df_grouped