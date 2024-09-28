# Fund Sweeping Bot for TON Blockchain

## Overview

The Fund Sweeping Bot automates the process of sweeping funds from a compromised wallet on the TON blockchain to a secure wallet. It dynamically checks balances for specified tokens and ensures sufficient gas fees in TON before performing any transactions. The bot reads configurations from JSON files to determine wallet addresses and token information.

## Prerequisites

Before running the bot, ensure you have the following:

1.  **Python 3.6 or higher**: The bot is built using Python, so you need a compatible version installed on your machine.
    
    -   You can download it from [Python's official website](https://www.python.org/downloads/).
2.  **Python Libraries**: The bot requires specific libraries to run. You can install these using `pip`:
    ```python
    `pip install requests` 
    ```
3.  **TON Center API Key**: You need a valid API key from TON Center to interact with the TON blockchain.
    
    -   Sign up at [TON Center](https://toncenter.com/) to obtain your API key.
4.  **JSON Configuration Files**:
    
    -   **config.json**: Contains wallet addresses, private key, and API details.
    -   **coinslist.json**: Lists the tokens you want to sweep, including their contract addresses.

### Example config.json
```json
`{
    "compromised_wallet_address": "YOUR_COMPROMISED_WALLET_ADDRESS",
    "new_wallet_address": "YOUR_NEW_WALLET_ADDRESS",
    "private_key": "COMPROMISED_WALLET_PRIVATE_KEY_OR_SEED_PHRASE",
    "toncenter_api_key": "YOUR_TONCENTER_API_KEY",
    "toncenter_api_url": "https://toncenter.com/api/v2",
    "sleep_interval_min": 5,
    "sleep_interval_max": 10
}` 
```
### Example coinslist.json
```json
`{
  "CATI": {
    "address": "EQD-cvR0Nz6XAyRBvbhz-abTrRC6sI5tvHvvpeQraV9UAAD7"
  },
  "TOKEN2": {
    "address": "YOUR_OTHER_TOKEN_ADDRESS"
  }
}` 
```
## Setup Instructions

1.  **Clone the Repository**: Download the bot code to your local machine. You can clone it using Git or download it as a ZIP file.
    ```bash    
    git clone <repository_url>
    cd <repository_directory>` 
    ```
2.  **Create Configuration Files**:
    
    -   Create a `config.json` file in the root directory of the project. Fill in the necessary details (wallet addresses, private key, and API key).
    -   Create a `coinslist.json` file to specify the tokens you want to sweep, using their respective addresses.
3.  **Install Dependencies**: Make sure to install the required libraries using pip as mentioned in the prerequisites.
    
4.  **Run the Bot**: Once everything is set up, you can run the bot using:
    ```python    
    `python ton-sweeper-bot.py` 
    ```
5.  **Monitor Output**: The bot will display logs in the console, showing its attempts to sweep funds and any errors encountered during execution.
    

## Important Notes

-   **Private Key Security**: Ensure that the private key for your compromised wallet is stored securely and not shared with anyone. Use this bot at your own risk.
-   **Testing**: It is advisable to test the bot in a safe environment (e.g., with minimal funds) before executing any significant transactions.
-   **API Rate Limits**: Be aware of the API rate limits imposed by TON Center. Frequent requests may lead to temporary bans.

## Troubleshooting

-   **Error Fetching Balances**: If you encounter errors while fetching balances, ensure your API key is valid and that you have internet access.
-   **Insufficient Funds for Gas Fees**: The bot requires a minimum amount of TON in the compromised wallet for transaction fees. Ensure that enough TON is available.

## Contributions

If you would like to contribute to the project, feel free to fork the repository and submit a pull request. Any suggestions or improvements are welcome!

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/amworx/TON-Sweeper-Bot/blob/8175da217b70c2eed1320dad0b859c8a982fb6f1/LICENSE) file for details.
