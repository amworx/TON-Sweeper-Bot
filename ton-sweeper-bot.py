import requests
import time
import random
import json
import os

# Load configuration from JSON file
def load_config():
    config_file = 'config.json'
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
            return (config['compromised_wallet_address'],
                    config['new_wallet_address'],
                    config['private_key'],
                    config['toncenter_api_key'],
                    config['sleep_interval_min'],
                    config['sleep_interval_max'])
    else:
        print("Configuration file not found!")
        return None

# Function to get live conversion rates from CoinGecko
def get_live_conversion_rates():
    # Define the tokens and their corresponding CoinGecko IDs
    tokens = {
        'TON': 'toncoin',
        'USD₮': 'tether',
        #'CATI': 'catizen',  # Updated CoinGecko ID for CATI
        #'HMSTR': 'hamster-kombat'  # Updated CoinGecko ID for HMSTR
    }
    
    # Fetch the current prices for the tokens
    url = 'https://api.coingecko.com/api/v3/simple/price'
    ids = ','.join(tokens.values())
    params = {
        'ids': ids,
        'vs_currencies': 'usd'  # Get prices in USD
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            conversion_rates = {token: data.get(token_id, {}).get('usd', 0) for token, token_id in tokens.items()}
            return conversion_rates
        else:
            print(f"Error fetching conversion rates: {response.status_code} - {response.text}")
            return {token: 0 for token in tokens}  # Return zero for all if there's an error
    except Exception as e:
        print(f"Exception while fetching conversion rates: {e}")
        return {token: 0 for token in tokens}  # Return zero for all if an exception occurs


# Function to convert token balances to USDT equivalent using live rates
def calculate_usdt_equivalent(balances):
    conversion_rates = get_live_conversion_rates()
    
    # Debug: Print the fetched conversion rates
    print(f"Conversion Rates: {conversion_rates}")
    
    total_usdt = 0
    for token, balance in balances.items():
        rate = conversion_rates.get(token, 0)
        
        # Debug: Print each token's balance and conversion rate
        print(f"Token: {token}, Balance: {balance}, Conversion Rate: {rate}")
        
        total_usdt += balance * rate
    
    return total_usdt


# Main function to execute the bot
def main():
    config = load_config()
    if config is None:
        return
    
    (compromised_wallet_address, new_wallet_address, 
     private_key, toncenter_api_key, 
     sleep_interval_min, sleep_interval_max) = config

    # Token tickers and their corresponding addresses
    tokens = {
        'TON': compromised_wallet_address,
        'USD₮': 'EQCxE6mUtQJKFnGfaROTKOt1lZbDiiX1kCixRv7Nw2Id_sDs',
        #'CATI': 'EQD-cvR0Nz6XAyRBvbhz-abTrRC6sI5tvHvvpeQraV9UAAD7',
        #'HMSTR': 'EQAJ8uWd7EBqsmpSWaRdf_I-8R8-XHwh3gsNKhy-UrdrPcUo'
    }

    # Function to get the balance of a specific token
    def get_balance(wallet_address, token):
        url = f'https://toncenter.com/api/v2/getAddressBalance?address={wallet_address}&token={token}&api_key={toncenter_api_key}'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                return int(data['result'])
            else:
                print(f"Warning: 'result' key not found in response for {token} ({wallet_address}). Full response: {data}")
                return 0
        else:
            print(f"Error fetching {token} balance for {wallet_address}: {response.status_code} - {response.text}")
            return 0

    # Function to get the TON balance specifically
    def get_ton_balance(wallet_address):
        url = f'https://toncenter.com/api/v2/getAddressBalance?address={wallet_address}&token=TON&api_key={toncenter_api_key}'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                if 'result' in data:
                    return int(data['result'])
                else:
                    print(f"Warning: 'result' key not found in response for TON ({wallet_address}). Full response: {data}")
                    return 0
            else:
                print(f"Error: API response not OK for TON ({wallet_address}). Full response: {data}")
                return 0
        else:
            print(f"Error fetching TON balance for {wallet_address}: {response.status_code} - {response.text}")
            return 0

    # Function to sweep funds
    def sweep_funds(token_address, token, amount):
        url = f'https://toncenter.com/api/v2/sweepFunds'
        payload = {
            'from': token_address,
            'to': new_wallet_address,
            'value': amount,
            'private_key': private_key,
            'token': token,
            'api_key': toncenter_api_key
        }
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                print(f"Successfully swept {amount} {token} from {token_address} to {new_wallet_address}.")
                return amount
            else:
                print(f"Error sweeping funds: {data['error']}")
        else:
            print(f"Error sweeping funds: {response.status_code} - {response.text}")
        return 0

    # Main process to check balances and sweep funds
    attempt_count = 0

    while True:
        print("Starting fund sweep process...")

        # Gather balances
        balances = {}
        for token, token_address in tokens.items():
            balance = get_balance(token_address, token)
            balances[token] = balance

        # Calculate total funds in USDT
        total_usdt = calculate_usdt_equivalent(balances)

        # Get TON balance for compromised wallet
        ton_balance = get_ton_balance(compromised_wallet_address)

        # Display the wallet information
        print(f"Wallet: {compromised_wallet_address}")
        print(f"Total fund in USDT: {total_usdt}")
        for token, balance in balances.items():
            print(f"{token}: {balance}")

        print(f"\nNew wallet: {new_wallet_address}")
        new_wallet_total_usdt = get_balance(new_wallet_address, 'USD₮')  # Assuming only USD₮ for new wallet balance
        print(f"Total fund in USDT: {new_wallet_total_usdt}")

        # Check for gas fees
        if ton_balance > 0:
            for token, token_address in tokens.items():
                balance = get_balance(token_address, token)

                if balance > 0:
                    attempt_count += 1
                    print(f"Attempting to sweep {balance} {token} from {token_address}...")
                    swept_amount = sweep_funds(token_address, token, balance)
                    if swept_amount > 0:
                        print(f"Swept amount: {swept_amount} {token}.")
        else:
            print("No gas fees in the compromised wallet to cover sweeping ...")

        # Random sleep interval
        sleep_time = random.randint(sleep_interval_min, sleep_interval_max)
        print(f"\nSleeping for {sleep_time} seconds...\n")
        time.sleep(sleep_time)

if __name__ == "__main__":
    main()
