import json
import os
from typing import Dict, Any

SETTINGS_FILE = "settings.json"

def load_settings() -> Dict[str, Any]:
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    else:
        return {
            "chain": "Sepolia",  # default
        }

def save_settings(settings: Dict[str, Any]) -> None:
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

# Chain configurations
CHAINS = {
    "sepolia": {
        "name": "Sepolia",
        "chain_id": 11155111,
        "rpc_url": os.getenv("SEPOLIA_RPC_URL", "https://sepolia.infura.io/v3/your-api-key"),
        "explorer_url": "https://sepolia.etherscan.io",
        "currency_symbol": "ETH",
        "network": "eth-sepolia"
    },
    "mainnet": {
        "name": "Mainnet",
        "chain_id": 1,
        "rpc_url": os.getenv("MAINNET_RPC_URL", "https://mainnet.infura.io/v3/your-api-key"),
        "explorer_url": "https://etherscan.io",
        "currency_symbol": "ETH",
        "network": "eth-mainnet"
    },
    "polygon": {
        "name": "Polygon",
        "chain_id": 137,
        "rpc_url": os.getenv("POLYGON_RPC_URL", "https://polygon-rpc.com"),
        "explorer_url": "https://polygonscan.com",
        "currency_symbol": "MATIC",
        "network": "polygon-mainnet"
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
    }
] 