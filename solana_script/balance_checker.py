from solana.rpc.api import Client
from solders.pubkey import Pubkey
import time
from typing import List
import json
import csv
import os

class SolanaBalanceChecker:
    def __init__(self, rpc_url: str = "https://api.mainnet-beta.solana.com"):
        """
        Initialize the Solana balance checker with an RPC URL
        """
        self.client = Client(rpc_url)

    def get_wallet_balance(self, wallet_address: str) -> float:
        """
        Get the balance of a single wallet address
        Returns balance in SOL
        """
        try:
            # Convert string address to Pubkey object
            pubkey = Pubkey(wallet_address)
            response = self.client.get_balance(pubkey)
            if response["result"]["value"] is not None:
                # Convert lamports to SOL (1 SOL = 1,000,000,000 lamports)
                balance_in_sol = response["result"]["value"] / 1_000_000_000
                return balance_in_sol
            return 0.0
        except Exception as e:
            print(f"Error checking balance for {wallet_address}: {str(e)}")
            return 0.0

    def check_multiple_wallets(self, wallet_addresses: List[str], delay: float = 0.5) -> dict:
        """
        Check balances for multiple wallet addresses
        Args:
            wallet_addresses: List of wallet addresses to check
            delay: Delay between requests in seconds to avoid rate limiting
        Returns:
            Dictionary with wallet addresses as keys and balances as values
        """
        results = {}
        for address in wallet_addresses:
            balance = self.get_wallet_balance(address)
            results[address] = balance
            time.sleep(delay)  # Add delay to avoid rate limiting
        return results

    def read_wallets_from_csv(self, csv_file: str) -> List[str]:
        """
        Read wallet addresses from a CSV file
        Args:
            csv_file: Path to the CSV file
        Returns:
            List of wallet addresses
        """
        wallets = []
        try:
            with open(csv_file, 'r') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    if row and row[0].strip():  # Check if row is not empty and address is not just whitespace
                        wallets.append(row[0].strip())
            return wallets
        except Exception as e:
            print(f"Error reading CSV file: {str(e)}")
            return []

    def save_results_to_csv(self, results: dict, output_file: str):
        """
        Save balance results to a CSV file
        Args:
            results: Dictionary of wallet addresses and their balances
            output_file: Path to save the output CSV file
        """
        try:
            with open(output_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Wallet Address', 'Balance (SOL)'])
                for address, balance in results.items():
                    writer.writerow([address, f"{balance:.4f}"])
            print(f"\nResults saved to {output_file}")
        except Exception as e:
            print(f"Error saving results to CSV: {str(e)}")

def main():
    # Initialize the checker
    checker = SolanaBalanceChecker()
    
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define input and output file paths
    input_file = os.path.join(script_dir, 'wallets.csv')
    output_file = os.path.join(script_dir, 'wallet_balances.csv')
    
    # Read wallets from CSV
    print(f"Reading wallets from {input_file}...")
    wallets = checker.read_wallets_from_csv(input_file)
    
    if not wallets:
        print("No valid wallet addresses found in the CSV file.")
        return
    
    print(f"Found {len(wallets)} wallet addresses to check.")
    print("Checking wallet balances...")
    
    # Check balances
    results = checker.check_multiple_wallets(wallets)
    
    # Print results
    print("\nWallet Balances:")
    print("-" * 50)
    for address, balance in results.items():
        print(f"Address: {address}")
        print(f"Balance: {balance:.4f} SOL")
        print("-" * 50)
    
    # Save results to CSV
    checker.save_results_to_csv(results, output_file)

if __name__ == "__main__":
    main()
