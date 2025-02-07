"""Deposits cash and orders bitcoin on Coinbase"""

from coinbase.rest import RESTClient
from dotenv import load_dotenv
from json import dumps
from cryptography.hazmat.primitives import serialization
import jwt
import requests
import time
import secrets
import os
import pprint

load_dotenv() # Loads the environment variables

USD_AMOUNT = 50    # USD to put into BTC
api_key = os.getenv('api_key')
api_secret = os.getenv('api_secret')
request_method = 'POST'
request_host   = "api.coinbase.com"
request_path   = f'/v2/accounts/{os.getenv("UUID")}/deposits'
deposit_endpoint = f'https://api.coinbase.com/v2/accounts/{os.getenv("UUID")}/deposits'

client = RESTClient(api_key=api_key, api_secret=api_secret)


def build_jwt(uri):
    private_key_bytes = api_secret.encode('utf-8')
    private_key = serialization.load_pem_private_key(private_key_bytes, password=None)
    jwt_payload = {
        'sub': api_key,
        'iss': "cdp",
        'nbf': int(time.time()),
        'exp': int(time.time()) + 120,
        'uri': uri,
    }
    jwt_token = jwt.encode(
        jwt_payload,
        private_key,
        algorithm='ES256',
        headers={'kid': api_key, 'nonce': secrets.token_hex()},
    )
    return jwt_token


def order_btc():
    order_id = 0
    with open('order_id.txt', "r+") as f:
        order_id = f.read()
        f.seek(0)
        f.write(str(int(order_id) + 1))

    order = client.market_order_buy(
        client_order_id=order_id,
        product_id="BTC-USD",
        quote_size=str(USD_AMOUNT))

    if order['success']:
        order_id = order['success_response']['order_id']
        print("BTC order successful")
    else:
        error_response = order['error_response']
        print(error_response)


def deposit_cash(jwt_token, amount):
    URL = deposit_endpoint
    payment_method = os.getenv('payment_method_id')
    headers = { 'Content-Type': 'application/json', 'Authorization': f'Bearer {jwt_token}', 'CB-VERSION': "2024-10-22", 'commit':'true'}
    payload = {'amount': str(amount), 'currency': 'USD', 'payment_method': payment_method}
    response = requests.post(URL, headers=headers, json=payload)
    if str(response.status_code).startswith('2'):
        print("Deposit successful")
    else:
        print("Error occurred while depositing funds. Error code: " + str(response.status_code))
    return response


def main():
    print("Attempting to purchase Bitcoin...")
    time.sleep(120)
    uri = f"{request_method} {request_host}{request_path}"
    jwt_token = build_jwt(uri)

    deposit_cash(jwt_token=jwt_token, amount=USD_AMOUNT)
    time.sleep(30)
    order_btc()
    time.sleep(5)
    

if __name__ == "__main__":
    main()
