from .services.chain_manager import ChainManager
from .services.wallet_manager import WalletManager
from .services.token_manager import TokenManager

# Initialize global instances
chain_manager = ChainManager()
wallet_manager = WalletManager()
token_manager = TokenManager(chain_manager.web3, chain_manager.chain_info) 