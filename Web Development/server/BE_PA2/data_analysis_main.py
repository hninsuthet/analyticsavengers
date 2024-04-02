from metrics import generate_metrics_auto
from clv_tiers import clv_tiers_auto
from summary_statistics import generate_sales_trends
from clv_months import get_monthly_clv
from customer_profiling import create_customer_profiling

def full_data_analysis(cleaned_data):

    # call generate_metrics_auto() from metrics.py
    metrics = generate_metrics_auto(cleaned_data)
    print(metrics.info())
    print('Done metrics')

    # call clv_tiers_auto() from clv_tiers.py
    clv_tier = clv_tiers_auto(cleaned_data)
    print('Done clv_tier')

    # # call generate_sales_trends() from summary_statistics.py
    # monthly_sales = generate_sales_trends(cleaned_data)
    # print('Done monthly_sales')

    # call get_monthly_clv() from clv_months.py
    monthly_clv_df = get_monthly_clv(cleaned_data)
    print(monthly_clv_df.info())
    print('Done monthly_clv_df')

    # call create_customer_profiling from clv_months.py
    customer_profiling_df = create_customer_profiling(cleaned_data)
    print('Done customer_profiling_df')

    # Convert dataframes to JSON format
    metrics_json = metrics.to_json(orient='records')
    clv_tier_json = clv_tier.to_json(orient='records')
    # monthly_sales_json = monthly_sales.to_json(orient='records')
    monthly_clv_df_json = monthly_clv_df.to_json(orient='records', default_handler=str)
    # monthly_clv_df_json = monthly_clv_df.to_json(orient='records')
    customer_profiling_df_json = customer_profiling_df.to_json(orient='records')

    # Create a dictionary to hold all JSON data
    response_data = {
        'metrics': metrics_json,
        'clv_tier': clv_tier_json,
        # 'monthly_sales': monthly_sales_json,
        'monthly_clv_df': monthly_clv_df_json,
        'customer_profiling_df':customer_profiling_df_json
    }

    # print(type(response_data))
    # Return JSON response
    return response_data

    # return (metrics, sales_trends)
    # pass