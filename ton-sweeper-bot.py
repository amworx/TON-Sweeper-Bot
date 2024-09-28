import requests
import json
import time
import random

# Load wallet data from config.json
with open('config.json') as config_file:
    config = json.load(config_file)

# Load coins list from coinslist.json
with open('coinslist.json') as coinslist_file:
    coins_list = json.load(coinslist_file)

# Function to get the balance of a wallet for a given token
def get_token_balance(wallet_address, token_address, api_key, api_url):
    url = f"{api_url}/getAddressBalance?address={wallet_address}&token={token_address}&api_key={api_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if 'balance' in data:
            return float(data['balance']) / (10**data.get('decimals', 9))  # Adjust for token decimals
    else:
        print(f"Error fetching balance for {wallet_address}: {response.status_code} - {response.text}")
    return 0

# Function to check TON balance
def get_ton_balance(wallet_address, api_key, api_url):
    url = f"{api_url}/getAddressBalance?address={wallet_address}&api_key={api_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if 'balance' in data:
            return float(data['balance']) / (10**9)  # TON has 9 decimals
    else:
        print(f"Error fetching TON balance for {wallet_address}: {response.status_code} - {response.text}")
    return 0

# Function to simulate sweeping process (replace with actual transaction logic)
def sweep_funds(wallet_address, new_wallet_address, token_name, balance):
    print(f"Sweeping {balance} {token_name} from {wallet_address} to {new_wallet_address}")
    # Add actual sweeping logic here
    return True

# Main sweeping process
def start_sweep():
    attempt_count = 0
    while True:
        attempt_count += 1
        print(f"\nStarting fund sweep process... Attempt: {attempt_count}")

        compromised_wallet = config['compromised_wallet_address']
        new_wallet = config['new_wallet_address']
        api_key = config['toncenter_api_key']
        api_url = config['toncenter_api_url']

        # Check gas fees (TON balance)
        ton_balance = get_ton_balance(compromised_wallet, api_key, api_url)
        print(f"Wallet: {compromised_wallet}, TON Balance: {ton_balance}")
        
        if ton_balance > 0.05:  # Ensure there's enough TON for transaction fees
            # Always sweep TON first
            if ton_balance > 0.05:
                if sweep_funds(compromised_wallet, new_wallet, 'TON', ton_balance - 0.05):
                    print(f"Successfully swept {ton_balance - 0.05} TON")

            # Sweep other coins dynamically from coinslist.json
            for token_name, token_info in coins_list.items():
                token_address = token_info['address']
                token_balance = get_token_balance(compromised_wallet, token_address, api_key, api_url)
                print(f"Wallet: {compromised_wallet}, {token_name} Balance: {token_balance}")
                
                if token_balance > 0:
                    if sweep_funds(compromised_wallet, new_wallet, token_name, token_balance):
                        print(f"Successfully swept {token_balance} {token_name}")
                else:
                    print(f"Wallet {compromised_wallet} does not have enough {token_name} for sweeping.")
        else:
            print(f"Not enough TON in the wallet for gas fees.")

        sleep_time = random.randint(config['sleep_interval_min'], config['sleep_interval_max'])
        print(f"Sleeping for {sleep_time} seconds...\n")
        time.sleep(sleep_time)

# Start the sweeping process
start_sweep()
