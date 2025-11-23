# EVM Transfer Bot API

A FastAPI-based REST API for managing EVM chain transfers, built on top of the original transfer_evmbot.py CLI application.

## Features

- Chain Management
  - Switch between different EVM chains
  - Get current chain information

- Wallet Management
  - Add/remove wallets
  - View wallet balances
  - Manage multiple wallets

- Token Operations
  - Transfer native tokens (ETH, MATIC, etc.)
  - Transfer ERC20 tokens
  - Transfer NFTs (ERC721)
  - Check token balances

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your configuration:
```env
SEPOLIA_RPC_URL=your_sepolia_rpc_url
MAINNET_RPC_URL=your_mainnet_rpc_url
POLYGON_RPC_URL=your_polygon_rpc_url
API_KEY=your_alchemy_api_key
```

4. Run the API:
```bash
uvicorn main:app --reload
```

## API Endpoints

### Chain Management
- `GET /api/chain/current` - Get current chain information
- `POST /api/chain/change/{chain_name}` - Change current chain

### Wallet Management
- `GET /api/wallet/all` - Get all wallets
- `POST /api/wallet/add` - Add a new wallet
- `DELETE /api/wallet/remove/{address}` - Remove a wallet
- `GET /api/wallet/balance/{address}` - Get wallet balance

### Token Operations
- `GET /api/token/erc20/balance/{wallet_address}/{token_address}` - Get ERC20 token balance
- `POST /api/token/erc20/transfer` - Transfer ERC20 tokens
- `GET /api/token/nft/tokens/{wallet_address}/{nft_address}` - Get NFT tokens
- `POST /api/token/nft/transfer` - Transfer NFT
- `POST /api/token/native/transfer` - Transfer native tokens

## Security Notes

- Never commit your `.env` file or private keys
- Use environment variables for sensitive information
- Consider implementing additional security measures for production use

## License

MIT License 