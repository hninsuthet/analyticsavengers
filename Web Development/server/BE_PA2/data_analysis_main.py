from metrics import generate_metrics_auto
from clv_tiers import clv_tiers_auto
from clv_months import get_monthly_clv
from customer_profiling import create_customer_profiling
from strategy import assign_discount_tiers, generate_loyal_strategy, generate_high_value_strategy

def full_data_analysis(cleaned_data):

    # call generate_metrics_auto() from metrics.py
    metrics = generate_metrics_auto(cleaned_data)
    print(metrics.info())
    print('Done metrics')

    # call clv_tiers_auto() from clv_tiers.py
    clv_tier = clv_tiers_auto(cleaned_data)
    print('Done clv_tier')

    # call get_monthly_clv() from clv_months.py
    monthly_clv_df = get_monthly_clv(cleaned_data)
    print(monthly_clv_df.info())
    print('Done monthly_clv_df')

    # call create_customer_profiling from clv_months.py
    customer_profiling_df = create_customer_profiling(cleaned_data)
    print('Done customer_profiling_df')

    # call assign_discount_tiers from strategy.py
    at_risk_strategy_df = assign_discount_tiers(cleaned_data)
    print('Done at_risk_strategy_df')
    
    # call generate_loyal_strategy from strategy.py
    loyal_strategy_df = generate_loyal_strategy(cleaned_data)
    print('Done loyal_strategy_df')

    # call generate_high_value_strategy from strategy.py
    high_value_strategy_df = generate_high_value_strategy(cleaned_data)
    print('Done high_value_strategy_df')

    # Convert dataframes to JSON format
    metrics_json = metrics.to_json(orient='records')
    clv_tier_json = clv_tier.to_json(orient='records')
    # monthly_sales_json = monthly_sales.to_json(orient='records')
    monthly_clv_df_json = monthly_clv_df.to_json(orient='records', default_handler=str)
    # monthly_clv_df_json = monthly_clv_df.to_json(orient='records')
    customer_profiling_df_json = customer_profiling_df.to_json(orient='records')
    at_risk_strategy_df_json = at_risk_strategy_df.to_json(orient='records')
    loyal_strategy_df_json = loyal_strategy_df.to_json(orient='records')
    high_value_strategy_df_json = high_value_strategy_df.to_json(orient='records')

    # Create a dictionary to hold all JSON data
    response_data = {
        'metrics': metrics_json,
        'clv_tier': clv_tier_json,
        # 'monthly_sales': monthly_sales_json,
        'monthly_clv_df': monthly_clv_df_json,
        'customer_profiling_df': customer_profiling_df_json,
        'at_risk_strategy_df': at_risk_strategy_df_json,
        'loyal_strategy_df': loyal_strategy_df_json,
        'high_value_strategy_df': high_value_strategy_df_json
    }

    # print(type(response_data))
    # Return JSON response
    return response_data

    # return (metrics, sales_trends)
    # pass