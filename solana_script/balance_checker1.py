import csv
from solana.rpc.api import Client
from solders.pubkey import Pubkey


# Initialize Solana client (you can change to mainnet if needed)
client = Client("https://api.mainnet-beta.solana.com")

input_file = "wallets.csv"
output_file = "wallet_balances.csv"

results = []

# Read wallet addresses from CSV
with open(input_file, "r") as f:
    reader = csv.reader(f)
    for row in reader:
        if not row:  # Skip empty rows
            continue
        address = row[0].strip()
        try:
            pubkey = Pubkey(address)
            balance_lamports = client.get_balance(pubkey)["result"]["value"]
            balance_sol = balance_lamports / 1e9  # Convert lamports to SOL
            results.append([address, balance_sol])
        except Exception as e:
            print(f"Error checking address {address}: {e}")
            results.append([address, "Error"])

# Write results to output CSV
with open(output_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Wallet Address", "Balance (SOL)"])
    writer.writerows(results)

print(f"Results saved to {output_file}")
