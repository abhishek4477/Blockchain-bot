from web3 import Web3
from dotenv import load_dotenv
import os

load_dotenv()

alchemy_url = os.getenv('ALCHEMY_URL_ETH')
web3 = Web3(Web3.HTTPProvider(alchemy_url))

if not web3.is_connected():
    print("Failed to connect to the Ethereum network")
    exit()

print("Connected to the Ethereum network")

sender_pk = os.getenv('SENDER_PK')
sender_address = web3.eth.account.from_key(sender_pk).address

nonce = web3.eth.get_transaction_count(sender_address)

def send_eth(reciever_address,value) :
    tx = {
    'nonce' : nonce,
    'from' : sender_address,
    'to' : reciever_address,
    'value' : value,
    'gas' : 21000,
    'gasPrice' : web3.to_wei('50','gwei'),
    }   

    signed_tx = web3.eth.account.sign_transaction(tx,sender_pk)
    send_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
    tx_hash = web3.to_hex(send_tx)

    print(f"Transaction sent: {tx_hash}")

def main():

    print("Welcome to the Ethereum Bot")
    user_input = input("Enter 1 to send ETH, 2 to exit: ").strip()
    if user_input == '1':
        reciever_address = input("Enter the reciever address: ").strip()
        amount = input("Enter the amount: ").strip()
        value = web3.to_wei(amount,'ether')
        send_eth(reciever_address,value)

    elif user_input == '2':
        print("Exiting...")
        return False
        
    else:
        print("Invalid option")
    
    return True

if __name__ == "__main__":
    while True:
        if not main():
            break

