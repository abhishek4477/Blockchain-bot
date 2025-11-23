from web3 import Web3
from typing import Dict, Any
from ..utils.helpers import load_settings, save_settings
from ..utils.helpers import CHAINS

class ChainManager:
    def __init__(self, default_chain: str = "sepolia"):
        settings = load_settings()
        saved_chain = settings.get("chain", default_chain).lower()
        
        if saved_chain not in CHAINS:
            saved_chain = default_chain
            settings["chain"] = saved_chain
            save_settings(settings)
            
        self.current_chain = saved_chain
        self.chain_info = CHAINS[self.current_chain]
        self.web3 = self._connect_web3()
    
    def _connect_web3(self) -> Web3:
        web3 = Web3(Web3.HTTPProvider(self.chain_info["rpc_url"]))
        return web3
    
    def change_chain(self, chain_name: str) -> Dict[str, Any]:
        chain_name = chain_name.lower()
        if chain_name not in CHAINS:
            return {"error": "Invalid chain name"}
        
        self.current_chain = chain_name
        self.chain_info = CHAINS[self.current_chain]
        self.web3 = self._connect_web3()
        
        settings = load_settings()
        settings["chain"] = self.current_chain
        save_settings(settings)
        
        return {
            "message": f"Successfully switched to {self.chain_info['name']}",
            "chain_info": {
                "name": self.chain_info["name"],
                "chain_id": self.chain_info["chain_id"],
                "currency_symbol": self.chain_info["currency_symbol"]
            }
        }
    
    def get_current_chain(self) -> Dict[str, Any]:
        return {
            "name": self.chain_info["name"],
            "chain_id": self.chain_info["chain_id"],
            "currency_symbol": self.chain_info["currency_symbol"]
        } 