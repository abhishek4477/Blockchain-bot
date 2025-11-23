#!/usr/bin/env python3
"""
EVM Transfer Bot - A modular tool for managing transfers across EVM-compatible chains
"""

import os
import json
import time
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple, Union
from dotenv import load_dotenv
from web3 import Web3
from web3.exceptions import ContractLogicError
import requests

# Load environment variables
load_dotenv()

SETTINGS_FILE = "settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    else:
        return {
            "chain": "Sepoolia",  # default
        }

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

# ------ Constants and Configuration ------

class ChainInfo:
    """Class for storing chain-specific information"""
    def __init__(self, name: str, chain_id: int, rpc_url: str, 
                explorer_url: str, currency_symbol: str, network: str):
        self.name = name
        self.chain_id = chain_id
        self.rpc_url = rpc_url
        self.explorer_url = explorer_url
        self.currency_symbol = currency_symbol
        self.network = network

# Chain configurations (dummy values, replace with actual values)
CHAINS = {
    "sepolia": ChainInfo(
        "Sepolia", 
        11155111, 
        os.getenv("SEPOLIA_RPC_URL", "https://sepolia.infura.io/v3/your-api-key"), 
        "https://sepolia.etherscan.io", 
        "ETH",
        "eth-sepolia"
    ),
    "Mainnet" : ChainInfo(
        "Mainnet",
        1,
        os.getenv("MAINNET_RPC_URL", "https://mainnet.infura.io/v3/your-api-key"),
        "https://etherscan.io",
        "ETH",
        "eth-mainnet"
    ),
    "Abstract" : ChainInfo(
        "Abstract",
        2741,
        os.getenv("ABSTRACT_RPC_URL", "https://mainnet.infura.io/v3/your-api-key"),
        "https://abscan.io",
        "ETH",
        "abstract-mainnet"
    ),
    "polygon": ChainInfo(
        "Polygon", 
        137, 
        os.getenv("POLYGON_RPC_URL", "https://polygon-rpc.com"), 
        "https://polygonscan.com", 
        "MATIC",
        "polygon-mainnet"
    ),
    "base": ChainInfo(
        "Base", 
        8453, 
        os.getenv("BASE_RPC_URL", "https://mainnet.base.org"), 
        "https://basescan.org", 
        "ETH",
        "base-mainnet"
    ),
    "arbitrum": ChainInfo(
        "Arbitrum", 
        42161, 
        os.getenv("ARBITRUM_RPC_URL", "https://arb1.arbitrum.io/rpc"), 
        "https://arbiscan.io", 
        "ETH",
        "arb-mainnet"
    ),
    "ape": ChainInfo(
        "ApeCoin", 
        40875, 
        os.getenv("APE_RPC_URL", "https://rpc.apecoin.chain"), 
        "https://explorer.apecoin.chain", 
        "APE",
        "ape-mainnet"
    )
}

# Common ERC20 tokens (dummy values)
COMMON_TOKENS = {
    "sepolia": {
        "USDC": "0xDummyUSDCSepolia",
        "USDT": "0xDummyUSDTSepolia"
    },
    "mainnet": {
        "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7"
    },
    "polygon": {
        "USDC": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
        "USDT": "0x3553f861dEc0257baDA9F8Ed268bf0D74e45E89C"
    },
    "base": {
        "USDC": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
        "USDT": "0xfde4C96c8593536E31F229EA8f37b2ADa2699bb2"
    },
    "arbitrum": {
        "USDC": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
        "USDT": "0xDummyUSDTArbitrum"
    },
    "ape": {
        "USDC": "0xDummyUSDCApeCoin",
        "USDT": "0xDummyUSDTApeCoin"
    }
}

# ERC20 ABI (minimal for our needs)
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# ERC721 ABI (minimal for our needs)
ERC721_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [
            {"name": "_owner", "type": "address"},
            {"name": "_index", "type": "uint256"}
        ],
        "name": "tokenOfOwnerByIndex",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_from", "type": "address"},
            {"name": "_to", "type": "address"},
            {"name": "_tokenId", "type": "uint256"}
        ],
        "name": "transferFrom",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_approved", "type": "bool"}
        ],
        "name": "setApprovalForAll",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# ------ Wallet Management ------

class WalletManager:
    """Class for handling wallet operations"""
    
    def __init__(self, wallets_file: str = "wallets.json"):
        self.wallets_file = wallets_file
        self.wallets = self._load_wallets()
        self.selected_wallets = []
    
    def _load_wallets(self) -> List[Dict[str, str]]:
        """Load wallets from JSON file"""
        try:
            with open(self.wallets_file, 'r') as f:
                wallets = json.load(f)
            return wallets
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Warning: Could not load wallets from {self.wallets_file}. Creating empty wallet list.")
            return []
    
    def save_wallets(self) -> None:
        """Save wallets to JSON file"""
        with open(self.wallets_file, 'w') as f:
            json.dump(self.wallets, f, indent=2)
    
    def add_wallet(self, name: str, address: str) -> None:
        """Add a new wallet"""
        # Check if wallet already exists
        for wallet in self.wallets:
            if wallet["address"].lower() == address.lower():
                print(f"Wallet with address {address} already exists.")
                return
        
        # Add new wallet
        self.wallets.append({"name": name, "address": address})
        self.save_wallets()
        print(f"Added wallet {name} with address {address}")
    
    def remove_wallet(self, address: str) -> None:
        """Remove a wallet by address"""
        self.wallets = [w for w in self.wallets if w["address"].lower() != address.lower()]
        self.save_wallets()
        print(f"Removed wallet with address {address}")
    
    def get_private_key(self, address: str) -> str:
        """Get private key for a wallet from environment variables"""
        key_name = f"PRIVATE_KEY_{address.upper()}"
        private_key = os.getenv(key_name)
        if not private_key:
            raise ValueError(f"Private key not found for address {address}. Ensure it's set in .env file as {key_name}")
        return private_key
    
    def select_wallets(self, web3_client) -> List[Dict[str, str]]:
        """Interactive function to select one or more wallets"""
        if not self.wallets:
            print("No wallets available. Please add wallets first.")
            return []
        
        print("\n=== Available Wallets ===")
        for i, wallet in enumerate(self.wallets, 1):
            address = wallet["address"]
            balance = web3_client.eth.get_balance(address)
            balance_eth = web3_client.from_wei(balance, 'ether')
            print(f"{i}. {wallet['name']} ({address}) - Balance: {balance_eth:.6f} {web3_client.chain_info.currency_symbol}")
        
        selected_indices = input("\nSelect wallet numbers (comma-separated, or 'all' for all): ").strip()
        
        if selected_indices.lower() == 'all':
            self.selected_wallets = self.wallets
            return self.wallets
        
        try:
            indices = [int(idx.strip()) - 1 for idx in selected_indices.split(',') if idx.strip()]
            self.selected_wallets = [self.wallets[i] for i in indices if 0 <= i < len(self.wallets)]
            return self.selected_wallets
        except (ValueError, IndexError):
            print("Invalid selection. Please enter valid wallet numbers.")
            return []
    
    def select_single_wallet(self, web3_client) -> Optional[Dict[str, str]]:
        """Select a single wallet interactively"""
        wallets = self.select_wallets(web3_client)
        if not wallets:
            return None
        
        if len(wallets) > 1:
            print("Multiple wallets selected. Using the first one.")
        
        return wallets[0]

# ------ Chain Management ------

class ChainManager:
    """Class for managing blockchain connections"""
    
    def __init__(self, default_chain: str = "sepolia"):
        # Load saved settings or use default
        settings = load_settings()
        saved_chain = settings.get("chain", default_chain)
        
        # Validate the saved chain exists in CHAINS
        if saved_chain.lower() not in [chain.lower() for chain in CHAINS.keys()]:
            print(f"Warning: Saved chain '{saved_chain}' not found. Using default chain '{default_chain}'")
            saved_chain = default_chain
            # Update settings with valid chain
            settings["chain"] = saved_chain
            save_settings(settings)
            
        self.current_chain = saved_chain
        self.chain_info = CHAINS[self.current_chain]
        self.web3 = self._connect_web3()
    
    def _connect_web3(self) -> Web3:
        """Initialize Web3 connection to the current chain"""
        web3 = Web3(Web3.HTTPProvider(self.chain_info.rpc_url))
        
        # Add chain_info attribute to web3 instance for convenience
        web3.chain_info = self.chain_info
        
        if not web3.is_connected():
            print(f"Warning: Could not connect to {self.chain_info.name}")
        else:
            print(f"Connected to {self.chain_info.name} (Chain ID: {self.chain_info.chain_id})")
            
        return web3
    
    def change_chain(self) -> None:
        """Interactive function to change the current chain"""
        print("\n=== Available Chains ===")
        chains = list(CHAINS.keys())
        for i, chain_id in enumerate(chains, 1):
            chain = CHAINS[chain_id]
            print(f"{i}. {chain.name} (Chain ID: {chain.chain_id})")
        
        try:
            selection = int(input("\nSelect chain number: ").strip())
            if 1 <= selection <= len(chains):
                self.current_chain = chains[selection - 1]
                self.chain_info = CHAINS[self.current_chain]
                self.web3 = self._connect_web3()
                
                # Save the new chain selection
                settings = load_settings()
                settings["chain"] = self.current_chain
                save_settings(settings)
            else:
                print("Invalid selection. Chain unchanged.")
        except ValueError:
            print("Invalid input. Chain unchanged.")

# ------ Token and Transfer Management ------

class TokenManager:
    """Class for handling token operations (ERC20, ERC721)"""
    
    def __init__(self, web3_client: Web3):
        self.web3 = web3_client
    
    def load_erc20_contract(self, token_address: str) -> Tuple[Any, Dict[str, Any]]:
        """Load an ERC20 token contract and return basic info"""
        contract = self.web3.eth.contract(address=token_address, abi=ERC20_ABI)
        
        try:
            # Fetch token info
            name = contract.functions.name().call()
            symbol = contract.functions.symbol().call()
            decimals = contract.functions.decimals().call()
            
            token_info = {
                "name": name,
                "symbol": symbol,
                "decimals": decimals,
                "address": token_address
            }
            
            print(f"\nLoaded token: {name} ({symbol})")
            print(f"Decimals: {decimals}")
            print(f"Contract: {token_address}")
            
            return contract, token_info
        except Exception as e:
            print(f"Error loading token contract: {e}")
            return None, {}
    
    def load_erc721_contract(self, nft_address: str) -> Tuple[Any, Dict[str, Any]]:
        """Load an ERC721 token contract and return basic info"""
        contract = self.web3.eth.contract(address=nft_address, abi=ERC721_ABI)
        
        try:
            # Fetch token info
            name = contract.functions.name().call()
            symbol = contract.functions.symbol().call()
            
            token_info = {
                "name": name,
                "symbol": symbol,
                "address": nft_address
            }
            
            print(f"\nLoaded NFT: {name} ({symbol})")
            print(f"Contract: {nft_address}")
            
            return contract, token_info
        except Exception as e:
            print(f"Error loading NFT contract: {e}")
            return None, {}
    
    def get_erc20_balance(self, wallet_address: str, contract) -> Tuple[int, float]:
        """Get ERC20 token balance for a wallet"""
        try:
            decimals = contract.functions.decimals().call()
            raw_balance = contract.functions.balanceOf(wallet_address).call()
            formatted_balance = raw_balance / (10 ** decimals)
            return raw_balance, formatted_balance
        except Exception as e:
            print(f"Error getting token balance: {e}")
            return 0, 0.0
    
    def get_nft_token_ids(self, wallet_address: str, contract):
        """Get NFT token IDs for a specific owner from a contract using Alchemy API"""
        # Validate inputs
        if not Web3.is_address(wallet_address):
            raise ValueError("Invalid owner address format")

        api_key = os.getenv("API_KEY")
        if not api_key:
            raise ValueError("API key is required")

        # Get contract address
        contract_address = contract.address if hasattr(contract, 'address') else contract
        if not Web3.is_address(contract_address):
            raise ValueError("Invalid contract address format")

        # Get network from current chain info
        network = self.web3.chain_info.network
        if not network:
            raise ValueError(f"No network identifier found for chain: {self.web3.chain_info.name}")

        url = f"https://{network}.g.alchemy.com/nft/v2/{api_key}/getNFTsForOwner"

        params = {
            "owner": wallet_address,
            "contractAddresses[]": contract_address,
            "withMetadata": "false"
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise exception for bad status codes
            
            data = response.json()
            if "error" in data:
                raise Exception(f"API Error: {data['error']}")
                
            nfts = data.get("ownedNfts", [])
            # Convert hex token IDs to integers
            token_ids = [int(nft["id"]["tokenId"], 16) for nft in nfts]
            return token_ids
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
            return []
        except (KeyError, ValueError) as e:
            print(f"Error parsing response: {str(e)}")
            return []
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return []

    def get_gas_parameters(self, web3_client, transaction_params, gas_estimate):
        """Get EIP-1559 gas parameters based on user's speed preference"""
        while True:
            print("\nSelect gas speed:")
            print("1. Slow (Lower priority fee)")
            print("2. Medium (Standard priority fee)")
            print("3. Fast (Higher priority fee)")
            
            try:
                speed_choice = int(input("Enter your choice (1-3): ").strip())
                if speed_choice not in [1, 2, 3]:
                    print("Invalid choice. Please enter 1, 2, or 3.")
                    continue
                
                # Get current base fee
                base_fee = web3_client.eth.get_block('latest')['baseFeePerGas']
                
                # Set priority fees based on speed
                if speed_choice == 1:  # Slow
                    priority_fee = web3_client.to_wei(0, 'gwei')  # 0 Gwei
                elif speed_choice == 2:  # Medium
                    priority_fee = web3_client.to_wei(0.5, 'gwei')  # 0.5 Gwei
                else:  # Fast
                    priority_fee = web3_client.to_wei(2, 'gwei')  # 2 Gwei
                
                # Calculate max fee (base fee + priority fee)
                max_fee = base_fee + priority_fee
                
                # Add buffer to gas estimate
                gas_limit = int(gas_estimate * 1.2)  # 20% buffer
                
                return {
                    'maxFeePerGas': max_fee,
                    'maxPriorityFeePerGas': priority_fee,
                    'gas': gas_limit,
                    'type': '0x2'  # EIP-1559 transaction type
                }
                
            except ValueError:
                print("Invalid input. Please enter a number between 1 and 3.")
                continue

    def send_native_token(self, sender_address: str, recipient_address: str, 
                          amount_in_ether: float, private_key: str) -> Optional[str]:
        """Send native tokens (ETH, MATIC, etc.) to a recipient"""
        try:
            # Convert amount to Wei
            amount_in_wei = self.web3.to_wei(amount_in_ether, 'ether')
            
            # Get the sender's nonce
            nonce = self.web3.eth.get_transaction_count(sender_address)
            
            # Build basic transaction
            tx = {
                'from': sender_address,
                'to': recipient_address,
                'value': amount_in_wei,
                'nonce': nonce,
                'chainId': self.web3.chain_info.chain_id
            }
            
            # Estimate gas
            gas_estimate = self.web3.eth.estimate_gas(tx)
            
            # Get EIP-1559 gas parameters
            gas_params = self.get_gas_parameters(self.web3, tx, gas_estimate)
            tx.update(gas_params)
            
            # Sign transaction
            signed_tx = self.web3.eth.account.sign_transaction(tx, private_key)
            
            # Send transaction
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            print(f"Transaction sent! Hash: {tx_hash.hex()}")
            print(f"View on explorer: {self.web3.chain_info.explorer_url}/tx/{tx_hash.hex()}")
            
            return tx_hash.hex()
        
        except Exception as e:
            print(f"Error sending transaction: {e}")
            return None
    
    def send_erc20_token(self, sender_address: str, contract, recipient_address: str, 
                         amount: float, token_info: Dict[str, Any], private_key: str) -> Optional[str]:
        """Send ERC20 tokens to a recipient"""
        try:
            # Convert amount to token units
            amount_in_units = int(amount * (10 ** token_info["decimals"]))
            
            # Build basic transaction
            txn = contract.functions.transfer(
                recipient_address,
                amount_in_units
            ).build_transaction({
                'from': sender_address,
                'nonce': self.web3.eth.get_transaction_count(sender_address),
                'chainId': self.web3.chain_info.chain_id
            })
            
            # Estimate gas
            gas_estimate = self.web3.eth.estimate_gas(txn)
            
            # Get EIP-1559 gas parameters
            gas_params = self.get_gas_parameters(self.web3, txn, gas_estimate)
            txn.update(gas_params)
            
            # Sign transaction
            signed_tx = self.web3.eth.account.sign_transaction(txn, private_key)
            
            # Send transaction
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            print(f"Transaction sent! Hash: {tx_hash.hex()}")
            print(f"View on explorer: {self.web3.chain_info.explorer_url}/tx/{tx_hash.hex()}")
            
            return tx_hash.hex()
        
        except Exception as e:
            print(f"Error sending ERC20 transaction: {e}")
            return None
    
    def send_nft(self, sender_address: str, contract, recipient_address: str, 
                token_id: int, private_key: str) -> Optional[str]:
        """Send NFT to a recipient"""
        try:
            # Build basic transaction
            txn = contract.functions.transferFrom(
                sender_address,
                recipient_address,
                token_id
            ).build_transaction({
                'from': sender_address,
                'nonce': self.web3.eth.get_transaction_count(sender_address),
                'chainId': self.web3.chain_info.chain_id
            })
            
            # Estimate gas
            gas_estimate = self.web3.eth.estimate_gas(txn)
            
            # Get EIP-1559 gas parameters
            gas_params = self.get_gas_parameters(self.web3, txn, gas_estimate)
            txn.update(gas_params)
            
            # Sign transaction
            signed_tx = self.web3.eth.account.sign_transaction(txn, private_key)
            
            # Send transaction
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            print(f"NFT transfer sent! Hash: {tx_hash.hex()}")
            print(f"View on explorer: {self.web3.chain_info.explorer_url}/tx/{tx_hash.hex()}")
            
            return tx_hash.hex()
        
        except Exception as e:
            print(f"Error sending NFT transaction: {e}")
            return None

# ------ Main Application ------

class TransferBot:
    """Main application class for the EVM Transfer Bot"""
    
    def __init__(self):
        self.chain_manager = ChainManager()
        self.wallet_manager = WalletManager()
        self.token_manager = TokenManager(self.chain_manager.web3)
    
    def check_balances(self) -> None:
        """Check native token balances for all wallets"""
        print("\n=== Wallet Balances ===")
        currency = self.chain_manager.chain_info.currency_symbol
        
        for wallet in self.wallet_manager.wallets:
            address = wallet["address"]
            balance = self.chain_manager.web3.eth.get_balance(address)
            balance_eth = self.chain_manager.web3.from_wei(balance, 'ether')
            print(f"{wallet['name']} ({address}): {balance_eth:.6f} {currency}")
    
    def disperse_native(self) -> None:
        """Send native tokens from one wallet to multiple recipients"""
        print("\n=== Disperse Native Tokens ===")
        
        while True:
            try:
                # Select sender wallet
                sender = self.wallet_manager.select_single_wallet(self.chain_manager.web3)
                if not sender:
                    print("No sender wallet selected. Please try again.")
                    continue
                
                sender_address = sender["address"]
                private_key = self.wallet_manager.get_private_key(sender_address)
                
                # Get sender balance
                balance = self.chain_manager.web3.eth.get_balance(sender_address)
                balance_eth = self.chain_manager.web3.from_wei(balance, 'ether')
                currency = self.chain_manager.chain_info.currency_symbol
                
                print(f"\nSender: {sender['name']} ({sender_address})")
                print(f"Available balance: {balance_eth:.6f} {currency}")
                
                # Get recipients
                while True:
                    recipients_input = input("\nEnter recipient addresses (comma-separated): ").strip()
                    recipients = [addr.strip() for addr in recipients_input.split(',') if addr.strip()]
                    
                    if not recipients:
                        print("No valid recipients provided.")
                        continue
                    
                    # Validate all addresses
                    invalid_addresses = [addr for addr in recipients if not self.chain_manager.web3.is_address(addr)]
                    if invalid_addresses:
                        print(f"Invalid addresses found: {', '.join(invalid_addresses)}")
                        print("Please enter valid Ethereum addresses.")
                        continue
                    break
                
                # Get amount per recipient
                while True:
                    try:
                        amount_input = input(f"\nAmount of {currency} to send to each recipient: ").strip()
                        amount_per_recipient = float(amount_input)
                        
                        if amount_per_recipient <= 0:
                            print("Amount must be greater than 0.")
                            continue
                        
                        total_amount = amount_per_recipient * len(recipients)
                        if total_amount > balance_eth:
                            print(f"Insufficient balance. Required: {total_amount:.6f} {currency}, Available: {balance_eth:.6f} {currency}")
                            continue
                        
                        print(f"\nYou are about to send {amount_per_recipient:.6f} {currency} to each of {len(recipients)} recipients.")
                        print(f"Total amount: {total_amount:.6f} {currency}")
                        
                        confirm = input("Confirm transaction (y/n): ").strip().lower()
                        if confirm != 'y':
                            print("Transaction cancelled.")
                            break
                        
                        # Get initial nonce
                        nonce = self.chain_manager.web3.eth.get_transaction_count(sender_address)
                        
                        # Send transactions
                        for recipient in recipients:
                            print(f"\nSending {amount_per_recipient:.6f} {currency} to {recipient}...")
                            
                            # Build transaction with current nonce
                            tx = {
                                'from': sender_address,
                                'to': recipient,
                                'value': self.chain_manager.web3.to_wei(amount_per_recipient, 'ether'),
                                'nonce': nonce,
                                'chainId': self.chain_manager.web3.chain_info.chain_id
                            }
                            
                            # Estimate gas
                            gas_estimate = self.chain_manager.web3.eth.estimate_gas(tx)
                            
                            # Get EIP-1559 gas parameters
                            gas_params = self.token_manager.get_gas_parameters(self.chain_manager.web3, tx, gas_estimate)
                            tx.update(gas_params)
                            
                            # Sign and send transaction
                            signed_tx = self.chain_manager.web3.eth.account.sign_transaction(tx, private_key)
                            tx_hash = self.chain_manager.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                            
                            if tx_hash:
                                print(f"Transaction successful: {tx_hash.hex()}")
                                nonce += 1  # Increment nonce for next transaction
                            else:
                                print("Transaction failed.")
                            
                            # Small delay between transactions
                            time.sleep(1)
                        
                        print("\nAll transactions completed.")
                        break
                        
                    except ValueError:
                        print("Invalid amount. Please enter a valid number.")
                        continue
                
                break  # Exit the main loop if everything completed successfully
                
            except Exception as e:
                print(f"An error occurred: {str(e)}")
                print("Please try again.")
                continue
    
    def merge_native(self) -> None:
        """Send native tokens from multiple wallets to one recipient"""
        print("\n=== Merge Native Tokens ===")
        
        while True:
            try:
                # Select sender wallets
                senders = self.wallet_manager.select_wallets(self.chain_manager.web3)
                if not senders:
                    print("No sender wallets selected. Please try again.")
                    continue
                
                # Select recipient
                while True:
                    recipient_input = input("\nEnter recipient address: ").strip()
                    if self.chain_manager.web3.is_address(recipient_input):
                        break
                    print("Invalid recipient address. Please enter a valid Ethereum address.")
                
                currency = self.chain_manager.chain_info.currency_symbol
                
                # Process each sender
                for sender in senders:
                    sender_address = sender["address"]
                    
                    try:
                        # Get balance
                        balance = self.chain_manager.web3.eth.get_balance(sender_address)
                        balance_eth = self.chain_manager.web3.from_wei(balance, 'ether')
                        
                        if balance_eth <= 0:
                            print(f"\nSkipping {sender['name']} ({sender_address}) - Zero balance")
                            continue
                        
                        # Reserve some for gas (0.001 ETH/MATIC/etc.)
                        reserve_for_gas = self.chain_manager.web3.to_wei(0.0001, 'ether')
                        available_to_send = max(0, balance - reserve_for_gas)
                        available_to_send_eth = self.chain_manager.web3.from_wei(available_to_send, 'ether')
                        
                        if available_to_send <= 0:
                            print(f"\nSkipping {sender['name']} ({sender_address}) - Insufficient balance for gas")
                            continue
                        
                        print(f"\nSender: {sender['name']} ({sender_address})")
                        print(f"Available balance: {balance_eth:.6f} {currency}")
                        print(f"Available to send (reserving 0.0001 {currency} for gas): {available_to_send_eth:.6f} {currency}")
                        
                        while True:
                            amount_input = input(f"Amount to send (or 'all' for maximum, 'skip' to skip): ").strip().lower()
                            
                            if amount_input == 'skip':
                                print(f"Skipping {sender['name']}")
                                break
                            
                            if amount_input == 'all':
                                amount_to_send = available_to_send_eth
                            else:
                                try:
                                    amount_to_send = float(amount_input)
                                except ValueError:
                                    print("Invalid amount. Please enter a number, 'all', or 'skip'.")
                                    continue
                            
                            if amount_to_send <= 0 or amount_to_send > available_to_send_eth:
                                print(f"Invalid amount. Must be between 0 and {available_to_send_eth:.6f}")
                                continue
                            
                            # Get private key and send
                            private_key = self.wallet_manager.get_private_key(sender_address)
                            print(f"Sending {amount_to_send:.6f} {currency} to {recipient_input}...")
                            
                            tx_hash = self.token_manager.send_native_token(
                                sender_address, recipient_input, amount_to_send, private_key
                            )
                            
                            if tx_hash:
                                print(f"Transaction successful: {tx_hash}")
                            else:
                                print("Transaction failed.")
                            
                            # Small delay between transactions
                            time.sleep(1)
                            break
                        
                    except Exception as e:
                        print(f"Error processing {sender['name']}: {str(e)}")
                        continue
                
                print("\nAll transactions completed.")
                break  # Exit the main loop if everything completed successfully
                
            except Exception as e:
                print(f"An error occurred: {str(e)}")
                print("Please try again.")
                continue
    
    def transfer_erc20(self, mode: str = "disperse") -> None:
        """Transfer ERC20 tokens (disperse or merge)"""
        print(f"\n=== {'Disperse' if mode == 'disperse' else 'Merge'} ERC20 Tokens ===")
        
        while True:
            try:
                # Step 1: Get token contract address
                print("\nOptions:")
                print("1. Use common token")
                print("2. Enter custom token address")
                print("3. Back to previous menu")
                
                token_option = input("Select option (1-3): ").strip()
                
                if token_option == "3":
                    return
                
                if token_option not in ["1", "2"]:
                    print("Invalid option. Please enter 1, 2, or 3.")
                    continue
                
                token_address = ""
                if token_option == "1":
                    # Show common tokens for the current chain
                    chain_id = self.chain_manager.current_chain
                    if chain_id in COMMON_TOKENS:
                        print("\nCommon tokens for this chain:")
                        tokens = list(COMMON_TOKENS[chain_id].items())
                        for i, (symbol, address) in enumerate(tokens, 1):
                            print(f"{i}. {symbol} ({address})")
                        
                        while True:
                            try:
                                token_idx = int(input("Select token number: ").strip())
                                if 1 <= token_idx <= len(tokens):
                                    _, token_address = tokens[token_idx - 1]
                                    break
                                print(f"Invalid selection. Please enter a number between 1 and {len(tokens)}.")
                            except ValueError:
                                print("Invalid input. Please enter a number.")
                    else:
                        print("No common tokens defined for this chain.")
                        continue
                else:
                    while True:
                        token_address = input("Enter token contract address: ").strip()
                        if self.chain_manager.web3.is_address(token_address):
                            break
                        print("Invalid address format. Please enter a valid Ethereum address.")
                
                # Load token contract
                contract, token_info = self.token_manager.load_erc20_contract(token_address)
                if not contract:
                    print("Failed to load token contract. Please try again.")
                    continue
                
                # Process based on mode
                if mode == "disperse":
                    # Select sender wallet
                    sender = self.wallet_manager.select_single_wallet(self.chain_manager.web3)
                    if not sender:
                        print("No sender wallet selected. Please try again.")
                        continue
                    
                    sender_address = sender["address"]
                    
                    # Get token balance
                    raw_balance, formatted_balance = self.token_manager.get_erc20_balance(sender_address, contract)
                    
                    print(f"\nSender: {sender['name']} ({sender_address})")
                    print(f"Token balance: {formatted_balance:.6f} {token_info['symbol']}")
                    
                    if formatted_balance <= 0:
                        print("Insufficient token balance.")
                        continue
                    
                    # Get recipients
                    while True:
                        recipients_input = input("\nEnter recipient addresses (comma-separated): ").strip()
                        recipients = [addr.strip() for addr in recipients_input.split(',') if addr.strip()]
                        
                        if not recipients:
                            print("No valid recipients provided.")
                            continue
                        
                        # Validate all addresses
                        invalid_addresses = [addr for addr in recipients if not self.chain_manager.web3.is_address(addr)]
                        if invalid_addresses:
                            print(f"Invalid addresses found: {', '.join(invalid_addresses)}")
                            print("Please enter valid Ethereum addresses.")
                            continue
                        break
                    
                    # Get amount per recipient
                    while True:
                        try:
                            amount_input = input(f"\nAmount of {token_info['symbol']} to send to each recipient: ").strip()
                            amount_per_recipient = float(amount_input)
                            
                            if amount_per_recipient <= 0:
                                print("Amount must be greater than 0.")
                                continue
                            
                            total_amount = amount_per_recipient * len(recipients)
                            if total_amount > formatted_balance:
                                print(f"Insufficient balance. Required: {total_amount:.6f} {token_info['symbol']}, Available: {formatted_balance:.6f} {token_info['symbol']}")
                                continue
                            
                            print(f"\nYou are about to send {amount_per_recipient:.6f} {token_info['symbol']} to each of {len(recipients)} recipients.")
                            print(f"Total amount: {total_amount:.6f} {token_info['symbol']}")
                            
                            confirm = input("Confirm transaction (y/n): ").strip().lower()
                            if confirm != 'y':
                                print("Transaction cancelled.")
                                break
                            
                            # Get private key
                            private_key = self.wallet_manager.get_private_key(sender_address)
                            
                            # Get initial nonce
                            nonce = self.chain_manager.web3.eth.get_transaction_count(sender_address)
                            
                            # Send transactions
                            for recipient in recipients:
                                print(f"\nSending {amount_per_recipient:.6f} {token_info['symbol']} to {recipient}...")
                                
                                # Convert amount to token units
                                amount_in_units = int(amount_per_recipient * (10 ** token_info["decimals"]))
                                
                                # Build transaction with current nonce
                                txn = contract.functions.transfer(
                                    recipient,
                                    amount_in_units
                                ).build_transaction({
                                    'from': sender_address,
                                    'nonce': nonce,
                                    'chainId': self.chain_manager.web3.chain_info.chain_id
                                })
                                
                                # Estimate gas
                                gas_estimate = self.chain_manager.web3.eth.estimate_gas(txn)
                                
                                # Get EIP-1559 gas parameters
                                gas_params = self.token_manager.get_gas_parameters(self.chain_manager.web3, txn, gas_estimate)
                                txn.update(gas_params)
                                
                                # Sign and send transaction
                                signed_tx = self.chain_manager.web3.eth.account.sign_transaction(txn, private_key)
                                tx_hash = self.chain_manager.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                                
                                if tx_hash:
                                    print(f"Transaction successful: {tx_hash.hex()}")
                                    nonce += 1  # Increment nonce for next transaction
                                else:
                                    print("Transaction failed.")
                                
                                # Small delay between transactions
                                time.sleep(1)
                            
                            print("\nAll transactions completed.")
                            break
                            
                        except ValueError:
                            print("Invalid amount. Please enter a valid number.")
                            continue
                
                else:  # mode == "merge"
                    # Select sender wallets
                    senders = self.wallet_manager.select_wallets(self.chain_manager.web3)
                    if not senders:
                        print("No sender wallets selected. Please try again.")
                        continue
                    
                    # Select recipient
                    while True:
                        recipient_input = input("\nEnter recipient address: ").strip()
                        if self.chain_manager.web3.is_address(recipient_input):
                            break
                        print("Invalid recipient address. Please enter a valid Ethereum address.")
                    
                    # Process each sender
                    for sender in senders:
                        sender_address = sender["address"]
                        
                        try:
                            # Get token balance
                            raw_balance, formatted_balance = self.token_manager.get_erc20_balance(sender_address, contract)
                            
                            if formatted_balance <= 0:
                                print(f"\nSkipping {sender['name']} ({sender_address}) - Zero token balance")
                                continue
                            
                            print(f"\nSender: {sender['name']} ({sender_address})")
                            print(f"Token balance: {formatted_balance:.6f} {token_info['symbol']}")
                            
                            while True:
                                amount_input = input(f"Amount to send (or 'all' for maximum, 'skip' to skip): ").strip().lower()
                                
                                if amount_input == 'skip':
                                    print(f"Skipping {sender['name']}")
                                    break
                                
                                if amount_input == 'all':
                                    amount_to_send = formatted_balance
                                else:
                                    try:
                                        amount_to_send = float(amount_input)
                                    except ValueError:
                                        print("Invalid amount. Please enter a number, 'all', or 'skip'.")
                                        continue
                                
                                if amount_to_send <= 0 or amount_to_send > formatted_balance:
                                    print(f"Invalid amount. Must be between 0 and {formatted_balance:.6f}")
                                    continue
                                
                                # Get private key and send
                                private_key = self.wallet_manager.get_private_key(sender_address)
                                print(f"Sending {amount_to_send:.6f} {token_info['symbol']} to {recipient_input}...")
                                
                                tx_hash = self.token_manager.send_erc20_token(
                                    sender_address, contract, recipient_input, amount_to_send, token_info, private_key
                                )
                                
                                if tx_hash:
                                    print(f"Transaction successful: {tx_hash}")
                                else:
                                    print("Transaction failed.")
                                
                                # Small delay between transactions
                                time.sleep(1)
                                break
                            
                        except Exception as e:
                            print(f"Error processing {sender['name']}: {str(e)}")
                            continue
                    
                    print("\nAll transactions completed.")
                
                break  # Exit the main loop if everything completed successfully
                
            except Exception as e:
                print(f"An error occurred: {str(e)}")
                print("Please try again.")
                continue
    
    def transfer_nft(self) -> None:
        """Transfer NFT tokens"""
        print("\n=== Transfer NFTs ===")
        
        while True:
            try:
                # Get NFT contract address
                nft_address = input("Enter NFT contract address: ").strip()
                if not self.chain_manager.web3.is_address(nft_address):
                    print("Invalid contract address. Please try again.")
                    continue
                
                # Load NFT contract
                contract, nft_info = self.token_manager.load_erc721_contract(nft_address)
                if not contract:
                    print("Failed to load NFT contract. Please try again.")
                    continue

                # Select recipient
                while True:
                    recipient_input = input("\nEnter recipient address: ").strip()
                    if self.chain_manager.web3.is_address(recipient_input):
                        break
                    print("Invalid recipient address. Please enter a valid Ethereum address.")

                # Select sender wallets
                senders = self.wallet_manager.select_wallets(self.chain_manager.web3)
                if not senders:
                    print("No sender wallets selected. Please try again.")
                    continue

                # Process each sender
                all_tokens = []  # List to store all token IDs with wallet info
                for sender in senders:
                    sender_address = sender["address"]
                    
                    try:
                        # Get NFT token IDs
                        token_ids = self.token_manager.get_nft_token_ids(sender_address, contract)
                        
                        if not token_ids:
                            print(f"\nSkipping {sender['name']} ({sender_address}) - No NFTs owned")
                            continue
                        
                        # Add tokens to the list with wallet info
                        for token_id in token_ids:
                            all_tokens.append({
                                'token_id': token_id,
                                'sender': sender,
                                'sender_address': sender_address
                            })
                        
                    except Exception as e:
                        print(f"Error getting tokens for {sender['name']}: {str(e)}")
                        continue
                
                if not all_tokens:
                    print("\nNo NFTs found in any of the selected wallets.")
                    return
                
                # Display all available tokens
                print("\n=== Available NFTs ===")
                for i, token_info in enumerate(all_tokens, 1):
                    print(f"{i}. Token ID: {token_info['token_id']} (Wallet: {token_info['sender']['name']})")
                
                # Get user selection
                while True:
                    selection = input("\nEnter token numbers to transfer (comma-separated, 'all', or 'skip'): ").strip().lower()
                    if selection == 'skip':
                        print("Operation cancelled.")
                        return
                    elif selection == 'all':
                        selected_tokens = all_tokens
                        break
                    else:
                        try:
                            indices = [int(x.strip()) - 1 for x in selection.split(',') if x.strip()]
                            if indices and all(0 <= i < len(all_tokens) for i in indices):
                                selected_tokens = [all_tokens[i] for i in indices]
                                break
                            print("Invalid token numbers. Please try again.")
                        except ValueError:
                            print("Invalid input. Please enter numbers, 'all', or 'skip'.")
                
                # Execute all transactions
                print("\nExecuting transfers...")
                for token_info in selected_tokens:
                    try:
                        token_id = token_info['token_id']
                        sender_address = token_info['sender_address']
                        sender_name = token_info['sender']['name']
                        
                        print(f"\nTransferring Token ID {token_id} from {sender_name}...")
                        
                        # Get private key
                        private_key = self.wallet_manager.get_private_key(sender_address)
                        
                        # Send transaction
                        tx_hash = self.token_manager.send_nft(
                            sender_address, contract, recipient_input, token_id, private_key
                        )
                        
                        if tx_hash:
                            print(f"Transfer successful: {tx_hash}")
                        else:
                            print("Transfer failed.")
                        
                        # Small delay between transactions
                        time.sleep(1)
                        
                    except Exception as e:
                        print(f"Error transferring Token ID {token_id}: {str(e)}")
                        continue
                
                print("\nAll transfers completed.")
                break  # Exit the main loop if everything completed successfully
                
            except Exception as e:
                print(f"An error occurred: {str(e)}")
                print("Please try again.")
                continue
    
    def merge_nft(self) -> None:
        """Merge NFTs from multiple wallets to one recipient"""
        print("\n=== Merge NFTs ===")
        
        # Get NFT contract address
        nft_address = input("Enter NFT contract address: ").strip()
        if not self.chain_manager.web3.is_address(nft_address):
            print("Invalid contract address. Please try again.")
            return

        # Load NFT contract
        contract, nft_info = self.token_manager.load_erc721_contract(nft_address)
        if not contract:
            print("Failed to load NFT contract. Please try again.")
            return

        # Select recipient
        while True:
            recipient_input = input("\nEnter recipient address: ").strip()
            if self.chain_manager.web3.is_address(recipient_input):
                break
            print("Invalid recipient address. Please enter a valid Ethereum address.")

        # Select sender wallets
        senders = self.wallet_manager.select_wallets(self.chain_manager.web3)
        if not senders:
            print("No sender wallets selected. Please try again.")
            return

        # Process each sender
        all_tokens = []  # List to store all token IDs with wallet info
        for sender in senders:
            try:
                # Get token IDs for this wallet
                token_ids = self.token_manager.get_nft_token_ids(sender["address"], contract)
                if token_ids:
                    all_tokens.extend([(token_id, sender) for token_id in token_ids])
            except Exception as e:
                print(f"Error getting token IDs for {sender['name']}: {str(e)}")
                continue

        if not all_tokens:
            print("No NFTs found in any of the selected wallets.")
            return

        # Display all available tokens
        print("\nAvailable NFTs:")
        for i, (token_id, sender) in enumerate(all_tokens, 1):
            print(f"{i}. Token ID: {token_id} (from {sender['name']})")

        # Get user selection
        while True:
            selection = input("\nEnter token numbers to transfer (comma-separated, 'all', or 'skip'): ").strip().lower()
            if selection == 'skip':
                return
            elif selection == 'all':
                selected_tokens = all_tokens
                break
            else:
                try:
                    indices = [int(x.strip()) - 1 for x in selection.split(',') if x.strip()]
                    if indices and all(0 <= i < len(all_tokens) for i in indices):
                        selected_tokens = [all_tokens[i] for i in indices]
                        break
                    print("Invalid token numbers. Please try again.")
                except ValueError:
                    print("Invalid input. Please enter numbers, 'all', or 'skip'.")

        # Execute all transactions
        print("\nExecuting transfers...")
        for token_id, sender in selected_tokens:
            try:
                # Get private key
                private_key = self.wallet_manager.get_private_key(sender["address"])
                
                # Send transaction
                tx_hash = self.token_manager.send_nft(
                    sender["address"],
                    contract,
                    recipient_input,
                    token_id,
                    private_key
                )

                if tx_hash:
                    print(f"Successfully transferred token {token_id} from {sender['name']}")
                    print(f"Transaction hash: {tx_hash}")
                else:
                    print(f"Failed to transfer token {token_id} from {sender['name']}")

                # Add delay between transactions
                time.sleep(2)

            except Exception as e:
                print(f"Error transferring token {token_id} from {sender['name']}: {str(e)}")
                continue
    
    def wallet_management(self) -> None:
        """Handle wallet management options"""
        while True:
            print("\n=== Wallet Management ===")
            print("1. View All Wallet Balances")
            print("2. Add New Wallet")
            print("3. Remove Wallet")
            print("4. Back to Main Menu")
            
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == "1":
                self.check_balances()
            elif choice == "2":
                name = input("Enter wallet name: ").strip()
                address = input("Enter wallet address: ").strip()
                self.wallet_manager.add_wallet(name, address)
                print("Don't forget to add the private key to your .env file!")
                print(f"Key format: PRIVATE_KEY_{address.upper()}=your_private_key")
            elif choice == "3":
                self.check_balances()
                address = input("Enter address of wallet to remove: ").strip()
                self.wallet_manager.remove_wallet(address)
            elif choice == "4":
                break
            else:
                print("Invalid option.")
    
    def run(self) -> None:
        """Run the main application loop"""
        print("\n" + "="*50)
        print("🚀 EVM Transfer Bot 🚀".center(50))
        print("="*50)
        
        while True:
            try:
                print("\n=== Main Menu ===")
                print(f"Current Chain: {self.chain_manager.chain_info.name}")
                print("\n1. Transfer Native Token")
                print("2. Transfer ERC20 Token")
                print("3. Transfer NFT (ERC721)")
                print("4. Wallet Management")
                print("5. Change Chain")
                print("6. Exit")
                
                while True:
                    choice = input("\nSelect option (1-6): ").strip()
                    if choice in ["1", "2", "3", "4", "5", "6"]:
                        break
                    print("Invalid option. Please enter a number between 1 and 6.")
                
                if choice == "1":
                    # Native token submenu
                    while True:
                        print("\n=== Native Token Transfer ===")
                        print("1. Disperse (One wallet to many recipients)")
                        print("2. Merge (Multiple wallets to one recipient)")
                        print("3. Back to Main Menu")
                        
                        sub_choice = input("\nSelect option (1-3): ").strip()
                        if sub_choice == "1":
                            self.disperse_native()
                            break
                        elif sub_choice == "2":
                            self.merge_native()
                            break
                        elif sub_choice == "3":
                            break
                        else:
                            print("Invalid option. Please enter a number between 1 and 3.")
                
                elif choice == "2":
                    # ERC20 token submenu
                    while True:
                        print("\n=== ERC20 Token Transfer ===")
                        print("1. Disperse (One wallet to many recipients)")
                        print("2. Merge (Multiple wallets to one recipient)")
                        print("3. Back to Main Menu")
                        
                        sub_choice = input("\nSelect option (1-3): ").strip()
                        if sub_choice == "1":
                            self.transfer_erc20(mode="disperse")
                            break
                        elif sub_choice == "2":
                            self.transfer_erc20(mode="merge")
                            break
                        elif sub_choice == "3":
                            break
                        else:
                            print("Invalid option. Please enter a number between 1 and 3.")
                
                elif choice == "3":
                    self.transfer_nft()
                
                elif choice == "4":
                    self.wallet_management()
                
                elif choice == "5":
                    self.chain_manager.change_chain()
                    # Update token manager with new web3 instance
                    self.token_manager = TokenManager(self.chain_manager.web3)
                
                elif choice == "6":
                    print("\nExiting EVM Transfer Bot. Goodbye!")
                    break
            
            except Exception as e:
                print(f"\nAn error occurred: {str(e)}")
                print("Returning to main menu...")
                continue


def main():
    """Entry point of the application"""
    load_settings()
    try:
        transfer_bot = TransferBot()
        transfer_bot.run()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Exiting...")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("Exiting application...")


if __name__ == "__main__":
    main()