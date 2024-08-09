import os
import json
import requests
import datetime
from urllib.parse import urlparse

# Environment variables
appsync_url = os.getenv('API_URL') 
appsync_api_key = os.getenv('API_KEY')  

def lambda_handler(event, context):
    stock_symbol = 'AAPL' 
    api_url = f'https://api.example.com/stock/{stock_symbol}/price'  

    # Fetch the stock price
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        stock_price = response.json()['price']
    except requests.RequestException as e:
        print(f"Error fetching stock price: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Error fetching stock price')
        }

    # GraphQL mutation to update DynamoDB via AppSync
    mutation = """
        mutation UpdateStockPrice($input: UpdateStockPriceInput!) {
            updateStockPrice(input: $input) {
                id
                symbol
                price
                timestamp
            }
        }
    """

    variables = {
        'input': {
            'id': '1', 
            'symbol': stock_symbol,
            'price': stock_price,
            'timestamp': datetime.datetime.utcnow().isoformat(),
        }
    }

    headers = {
        'Content-Type': 'application/json',
        'x-api-key': appsync_api_key,
    }

    parsed_url = urlparse(appsync_url)
    appsync_endpoint = f'{parsed_url.scheme}://{parsed_url.netloc}/graphql'

    try:
        response = requests.post(appsync_endpoint, json={'query': mutation, 'variables': variables}, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        print("AppSync response:", response.json())
    except requests.RequestException as e:
        print(f"Error updating stock price in AppSync: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Error updating stock price in AppSync')
        }

    return {
        'statusCode': 200,
        'body': json.dumps('Success')
    }
