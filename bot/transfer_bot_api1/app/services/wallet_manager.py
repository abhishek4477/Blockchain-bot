import json
import os
from typing import List, Dict, Any, Optional
from ..utils.helpers import load_settings

class WalletManager:
    def __init__(self, wallets_file: str = "wallets.json"):
        self.wallets_file = wallets_file
        self.wallets = self._load_wallets()
    
    def _load_wallets(self) -> List[Dict[str, str]]:
        try:
            with open(self.wallets_file, 'r') as f:
                wallets = json.load(f)
            return wallets
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_wallets(self) -> None:
        with open(self.wallets_file, 'w') as f:
            json.dump(self.wallets, f, indent=2)
    
    def add_wallet(self, name: str, address: str) -> Dict[str, Any]:
        for wallet in self.wallets:
            if wallet["address"].lower() == address.lower():
                return {"error": f"Wallet with address {address} already exists"}
        
        self.wallets.append({"name": name, "address": address})
        self.save_wallets()
        return {"message": f"Added wallet {name} with address {address}"}
    
    def remove_wallet(self, address: str) -> Dict[str, Any]:
        initial_length = len(self.wallets)
        self.wallets = [w for w in self.wallets if w["address"].lower() != address.lower()]
        if len(self.wallets) == initial_length:
            return {"error": f"No wallet found with address {address}"}
        
        self.save_wallets()
        return {"message": f"Removed wallet with address {address}"}
    
    def get_private_key(self, address: str) -> Optional[str]:
        key_name = f"PRIVATE_KEY_{address.upper()}"
        return os.getenv(key_name)
    
    def get_all_wallets(self) -> List[Dict[str, str]]:
        return self.wallets
    
    def get_wallet_balance(self, web3, address: str) -> Dict[str, Any]:
        try:
            balance = web3.eth.get_balance(address)
            balance_eth = web3.from_wei(balance, 'ether')
            return {
                "address": address,
                "balance": float(balance_eth),
                "currency": web3.chain_info.currency_symbol
            }
        except Exception as e:
            return {"error": str(e)} 