import requests
import dotenv
import os
from web3 import Web3

dotenv.load_dotenv()

# def get_nft_owners(contract_address, api_key, network="abstract-mainnet"):
#     url = f"https://{network}.g.alchemy.com/nft/v2/{api_key}/getOwnersForCollection"

#     params = {
#         "contractAddress": contract_address,
#         "withTokenBalances": "false"
#     }

#     try:
#         response = requests.get(url, params=params)
#         response.raise_for_status()
#         data = response.json()
#         return data.get("ownerAddresses", [])
#     except Exception as e:
#         print(f"Error: {e}")
#         return []

# # Example usage
# API_KEY = "xv_1yyDNHa0rAGYTeifyifofXb0t92oK"
# contract = "0xa6C46c07F7f1966D772E29049175EBBa26262513"

# owners = get_nft_owners(contract, API_KEY)
# print("Owners:", owners)

def get_token_ids(contract_address, owner_address, api_key, network="eth-mainnet"):
    """Get NFT token IDs for a specific owner from a contract using Alchemy API"""
    # Validate inputs
    if not Web3.is_address(contract_address):
        raise ValueError("Invalid contract address format")
    if not Web3.is_address(owner_address):
        raise ValueError("Invalid owner address format")
    if not api_key:
        raise ValueError("API key is required")

    url = f"https://{network}.g.alchemy.com/nft/v2/{api_key}/getNFTsForOwner"

    params = {
        "owner": owner_address,
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

def main():
    try:
        contract_address = input("Enter the contract address: ").strip()
        owner_address = input("Enter the owner address: ").strip()
        API_KEY = os.getenv("API_KEY")
        
        if not API_KEY:
            print("Error: API_KEY not found in environment variables")
            return
            
        token_ids = get_token_ids(contract_address, owner_address, API_KEY, network="eth-mainnet")

        print(token_ids)
        
    #     if token_ids:
    #         print("\nToken IDs found:")
    #         for token_id in token_ids:
    #             print(f"- {token_id}")
    #     else:
    #         print("\nNo token IDs found or an error occurred.")
            
    except ValueError as e:
        print(f"Input error: {str(e)}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()


#0xe17827609ac34443b3987661f4e037642f6bd9ba (CA shellorbz)
