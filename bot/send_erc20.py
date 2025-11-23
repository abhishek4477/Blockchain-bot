from web3 import Web3
from dotenv import load_dotenv
import os
from eth_utils import to_checksum_address

load_dotenv()

alchemy_url = os.getenv('ALCHEMY_URL_ETH')
web3 = Web3(Web3.HTTPProvider(alchemy_url))

if not web3.is_connected():
    print("Failed to connect to the Ethereum network")
    exit()

print("Connected to the Ethereum network")

# ERC20 ABI for decimals and transfer
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
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
        "type": "function"
    }
]

def transfer_erc20(token_contract: str, receiver_address: str, value: float) -> str:
    """
    Transfer ERC20 tokens from one wallet to another
    
    Args:
        token_contract (str): The ERC20 token contract address
        receiver_address (str): The address to receive the tokens
        value (float): The amount of tokens to transfer
        private_key (str): The private key of the sender's wallet
    
    Returns:
        str: Transaction hash if successful
    
    Raises:
        Exception: If any error occurs during the transfer
    """
    try:
        # Convert addresses to checksum format
        token_contract = to_checksum_address(token_contract)
        receiver_address = to_checksum_address(receiver_address)
        
        private_key = os.getenv('SENDER_PK')
        
        # Create contract instance
        contract = web3.eth.contract(address=token_contract, abi=ERC20_ABI)
        
        # Get token decimals
        decimals = contract.functions.decimals().call()
        
        # Convert value to token units (considering decimals)
        token_amount = int(value * (10 ** decimals))
        
        # Get sender's address from private key
        sender_address = web3.eth.account.from_key(private_key).address
        
        # Get nonce
        nonce = web3.eth.get_transaction_count(sender_address)
        
        # Build transaction
        transaction = contract.functions.transfer(
            receiver_address,
            token_amount
        ).build_transaction({
            'from': sender_address,
            'nonce': nonce,
            'gas': 200000,  # Adjust gas limit as needed
            'gasPrice': web3.eth.gas_price
        })
        
        # Sign transaction
        signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
        
        # Send transaction
        tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        
        # Wait for transaction receipt
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        
        # Convert transaction hash to hex with 0x prefix
        tx_hash_hex = web3.to_hex(receipt.transactionHash)
        return tx_hash_hex
        
    except Exception as e:
        raise Exception(f"Error transferring tokens: {str(e)}")

if __name__ == "__main__":
    print("\n=== ERC20 Token Transfer ===")
    
    # Get token contract address
    token_contract = input("\nEnter the token contract address: ").strip()
    
    # Get receiver address
    receiver_address = input("Enter the receiver's address: ").strip()
    
    # Get amount to transfer
    while True:
        try:
            value = float(input("Enter the amount of tokens to transfer: ").strip())
            if value <= 0:
                print("Amount must be greater than 0")
                continue
            break
        except ValueError:
            print("Please enter a valid number")
    
    try:
        print("\nInitiating transfer...")
        tx_hash = transfer_erc20(token_contract, receiver_address, value)
        print(f"\nTransfer successful!")
        print(f"Transaction hash: {tx_hash}")
        print(f"View on Etherscan: https://sepolia.etherscan.io/tx/{tx_hash}")
    except Exception as e:
        print(f"\nError: {str(e)}")

