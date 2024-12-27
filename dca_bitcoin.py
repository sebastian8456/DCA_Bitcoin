"""Orders bitcoin"""
USD_AMOUNT = 5

from coinbase.rest import RESTClient
from dotenv import load_dotenv
from json import dumps
import os

load_dotenv()

api_key = os.getenv('api_key')
api_secret = os.getenv('api_secret')

client = RESTClient(api_key=api_key, api_secret=api_secret)

order_id = 0
with open('order_id.txt', "r+") as f:
    order_id = f.read()
    f.seek(0)
    f.write(str(int(order_id) + 1))

order = client.market_order_buy(
    client_order_id=order_id,
    product_id="BTC-USD",
    quote_size=USD_AMOUNT)

if order['success']:
    order_id = order['success_response']['order_id']
    fills = client.get_fills(order_id=order_id)
    print(dumps(fills.to_dict(), indent=2))
else:
    error_response = order['error_response']
    print(error_response)