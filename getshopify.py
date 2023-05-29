# -*- coding: utf-8 -*-
"""Untitled1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1qH8wo8epwDWuakMyHnE6VFklY-9XCQfj
"""

def get_shopify(day=30):
    import requests
    import datetime
    import time
    api_key = "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"
    store_name = "kyari-co"
    api_version = "2023-04"

    orders = []
    last_order_id = 2500
    is_last_page = False

    created_at_min = (datetime.datetime.now() - datetime.timedelta(days=day)).strftime("%Y-%m-%d")

    while not is_last_page:
        endpoint = f"/admin/api/{api_version}/orders.json?status=any"
        api_url = f"https://{store_name}.myshopify.com{endpoint}&created_at_min={created_at_min}&limit=250&since_id={last_order_id}"
        
        headers = {
            "X-Shopify-Access-Token": api_key,
            "Accept": "application/json",
        }

        response = requests.get(api_url, headers=headers)
        json_data = response.json()
        orders_on_page = json_data["orders"]

        if len(orders_on_page) == 0:
            is_last_page = True
        else:
            orders.extend(orders_on_page)
            last_order_id = orders_on_page[-1]["id"]

        time.sleep(0.5)  # Add a delay between API requests to respect rate limits

    return orders