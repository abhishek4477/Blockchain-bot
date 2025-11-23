from typing import Dict, Any, Tuple, Optional
from web3 import Web3
import requests
import os
from ..utils.helpers import ERC20_ABI, ERC721_ABI

class TokenManager:
    def __init__(self, web3_client: Web3, chain_info: Dict[str, Any]):
        self.web3 = web3_client
        self.chain_info = chain_info
    
    def load_erc20_contract(self, token_address: str) -> Tuple[Any, Dict[str, Any]]:
        contract = self.web3.eth.contract(address=token_address, abi=ERC20_ABI)
        try:
            name = contract.functions.name().call()
            symbol = contract.functions.symbol().call()
            decimals = contract.functions.decimals().call()
            
            token_info = {
                "name": name,
                "symbol": symbol,
                "decimals": decimals,
                "address": token_address
            }
            
            return contract, token_info
        except Exception as e:
            return None, {"error": str(e)}
    
    def load_erc721_contract(self, nft_address: str) -> Tuple[Any, Dict[str, Any]]:
        contract = self.web3.eth.contract(address=nft_address, abi=ERC721_ABI)
        try:
            name = contract.functions.name().call()
            symbol = contract.functions.symbol().call()
            
            token_info = {
                "name": name,
                "symbol": symbol,
                "address": nft_address
            }
            
            return contract, token_info
        except Exception as e:
            return None, {"error": str(e)}
    
    def get_erc20_balance(self, wallet_address: str, contract) -> Dict[str, Any]:
        try:
            decimals = contract.functions.decimals().call()
            raw_balance = contract.functions.balanceOf(wallet_address).call()
            formatted_balance = raw_balance / (10 ** decimals)
            return {
                "raw_balance": raw_balance,
                "formatted_balance": float(formatted_balance)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_nft_token_ids(self, wallet_address: str, contract) -> Dict[str, Any]:
        try:
            api_key = os.getenv("API_KEY")
            if not api_key:
                return {"error": "API key is required"}
            
            contract_address = contract.address if hasattr(contract, 'address') else contract
            
            url = f"https://{self.chain_info['network']}.g.alchemy.com/nft/v2/{api_key}/getNFTsForOwner"
            
            params = {
                "owner": wallet_address,
                "contractAddresses[]": contract_address,
                "withMetadata": "false"
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if "error" in data:
                return {"error": data["error"]}
            
            nfts = data.get("ownedNfts", [])
            token_ids = [int(nft["id"]["tokenId"], 16) for nft in nfts]
            return {"token_ids": token_ids}
            
        except Exception as e:
            return {"error": str(e)}
    
    def send_native_token(self, sender_address: str, recipient_address: str, 
                         amount_in_ether: float, private_key: str) -> Dict[str, Any]:
        try:
            amount_in_wei = self.web3.to_wei(amount_in_ether, 'ether')
            nonce = self.web3.eth.get_transaction_count(sender_address)
            
            tx = {
                'from': sender_address,
                'to': recipient_address,
                'value': amount_in_wei,
                'nonce': nonce,
                'chainId': self.chain_info["chain_id"]
            }
            
            gas_estimate = self.web3.eth.estimate_gas(tx)
            gas_params = self.get_gas_parameters(self.web3, tx, gas_estimate)
            tx.update(gas_params)
            
            signed_tx = self.web3.eth.account.sign_transaction(tx, private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            return {
                "success": True,
                "tx_hash": tx_hash.hex(),
                "explorer_url": f"{self.chain_info['explorer_url']}/tx/{tx_hash.hex()}"
            }
        
        except Exception as e:
            return {"error": str(e)}
    
    def send_erc20_token(self, sender_address: str, contract, recipient_address: str, 
                        amount: float, token_info: Dict[str, Any], private_key: str) -> Dict[str, Any]:
        try:
            amount_in_units = int(amount * (10 ** token_info["decimals"]))
            
            txn = contract.functions.transfer(
                recipient_address,
                amount_in_units
            ).build_transaction({
                'from': sender_address,
                'nonce': self.web3.eth.get_transaction_count(sender_address),
                'chainId': self.chain_info["chain_id"]
            })
            
            gas_estimate = self.web3.eth.estimate_gas(txn)
            gas_params = self.get_gas_parameters(self.web3, txn, gas_estimate)
            txn.update(gas_params)
            
            signed_tx = self.web3.eth.account.sign_transaction(txn, private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            return {
                "success": True,
                "tx_hash": tx_hash.hex(),
                "explorer_url": f"{self.chain_info['explorer_url']}/tx/{tx_hash.hex()}"
            }
        
        except Exception as e:
            return {"error": str(e)}
    
    def send_nft(self, sender_address: str, contract, recipient_address: str, 
                token_id: int, private_key: str) -> Dict[str, Any]:
        try:
            txn = contract.functions.transferFrom(
                sender_address,
                recipient_address,
                token_id
            ).build_transaction({
                'from': sender_address,
                'nonce': self.web3.eth.get_transaction_count(sender_address),
                'chainId': self.chain_info["chain_id"]
            })
            
            gas_estimate = self.web3.eth.estimate_gas(txn)
            gas_params = self.get_gas_parameters(self.web3, txn, gas_estimate)
            txn.update(gas_params)
            
            signed_tx = self.web3.eth.account.sign_transaction(txn, private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw)
            
            return {
                "success": True,
                "tx_hash": tx_hash.hex(),
                "explorer_url": f"{self.chain_info['explorer_url']}/tx/{tx_hash.hex()}"
            }
        
        except Exception as e:
            return {"error": str(e)}
    
    def get_gas_parameters(self, web3_client, transaction_params, gas_estimate):
        base_fee = web3_client.eth.get_block('latest')['baseFeePerGas']
        priority_fee = web3_client.to_wei(0.5, 'gwei')  # Default to medium priority
        max_fee = base_fee + priority_fee
        gas_limit = int(gas_estimate * 1.2)  # 20% buffer
        
        return {
            'maxFeePerGas': max_fee,
            'maxPriorityFeePerGas': priority_fee,
            'gas': gas_limit,
            'type': '0x2'
        } 