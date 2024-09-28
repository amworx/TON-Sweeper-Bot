import requests
import json
import time
import random
import threading

# Load wallet data from config.json
with open('config.json') as config_file:
    config = json.load(config_file)

# Load API keys from api.json
with open('api.json') as api_file:
    api_keys = json.load(api_file)

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

# Function to sign and send the transaction
def sweep_funds(wallet_address, new_wallet_address, token_name, balance, private_key, api_key, api_url):
    print(f"Sweeping {balance} {token_name} from {wallet_address} to {new_wallet_address}")
    # Replace with actual transaction logic (signing and sending the transaction)
    tx_data = {
        "from": wallet_address,
        "to": new_wallet_address,
        "amount": balance,
        "token": token_name,
        "private_key": private_key
    }

    # Sign and send the transaction via your API
    url = f"{api_url}/sendTransaction"  # Example endpoint
    response = requests.post(url, json=tx_data, headers={"api_key": api_key})

    if response.status_code == 200:
        print(f"Successfully swept {balance} {token_name}")
        return True
    else:
        print(f"Error sending transaction: {response.status_code} - {response.text}")
        return False

# Function to perform the sweeping process for a specific API key
def sweep_with_api_key(api_key_info):
    api_key = api_key_info['api_key']
    api_url = api_key_info['api_url']

    compromised_wallet = config['compromised_wallet_address']
    new_wallet = config['new_wallet_address']
    private_key = config['private_key']

    # Check gas fees (TON balance)
    ton_balance = get_ton_balance(compromised_wallet, api_key, api_url)
    print(f"Wallet: {compromised_wallet}, TON Balance: {ton_balance}")
    
    if ton_balance > 0.05:  # Ensure there's enough TON for transaction fees
        # Always sweep TON first
        if ton_balance > 0.05:
            if sweep_funds(compromised_wallet, new_wallet, 'TON', ton_balance - 0.05, private_key, api_key, api_url):
                print(f"Successfully swept {ton_balance - 0.05} TON")

        # Sweep other coins dynamically from coinslist.json
        for token_name, token_info in coins_list.items():
            token_address = token_info['address']
            token_balance = get_token_balance(compromised_wallet, token_address, api_key, api_url)
            print(f"Wallet: {compromised_wallet}, {token_name} Balance: {token_balance}")
            
            if token_balance > 0:
                if sweep_funds(compromised_wallet, new_wallet, token_name, token_balance, private_key, api_key, api_url):
                    print(f"Successfully swept {token_balance} {token_name}")
            else:
                print(f"Wallet {compromised_wallet} does not have enough {token_name} for sweeping.")
    else:
        print(f"Not enough TON in the wallet for gas fees.")

# Main sweeping process
def start_sweep():
    attempt_count = 0
    while True:
        attempt_count += 1
        print(f"\nStarting fund sweep process... Attempt: {attempt_count}")

        threads = []
        for api in api_keys:
            thread = threading.Thread(target=sweep_with_api_key, args=(api,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        sleep_time = random.randint(config['sleep_interval_min'], config['sleep_interval_max'])
        print(f"Sleeping for {sleep_time} seconds...\n")
        time.sleep(sleep_time)

# Start the sweeping process
start_sweep()
