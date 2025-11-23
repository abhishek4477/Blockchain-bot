from flask import Blueprint, jsonify, request
from .. import token_manager, wallet_manager, chain_manager

bp = Blueprint('token', __name__)

@bp.route('/erc20/balance/<wallet_address>/<token_address>', methods=['GET'])
def get_erc20_balance(wallet_address, token_address):
    contract, token_info = token_manager.load_erc20_contract(token_address)
    if not contract:
        return jsonify(token_info), 400
    
    result = token_manager.get_erc20_balance(wallet_address, contract)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)

@bp.route('/erc20/transfer', methods=['POST'])
def transfer_erc20():
    data = request.get_json()
    if not data or not all(k in data for k in ['sender_address', 'recipient_address', 'amount', 'private_key', 'token_address']):
        return jsonify({"error": "Missing required fields"}), 400
    
    contract, token_info = token_manager.load_erc20_contract(data['token_address'])
    if not contract:
        return jsonify(token_info), 400
    
    result = token_manager.send_erc20_token(
        data['sender_address'],
        contract,
        data['recipient_address'],
        data['amount'],
        token_info,
        data['private_key']
    )
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)

@bp.route('/nft/tokens/<wallet_address>/<nft_address>', methods=['GET'])
def get_nft_tokens(wallet_address, nft_address):
    contract, nft_info = token_manager.load_erc721_contract(nft_address)
    if not contract:
        return jsonify(nft_info), 400
    
    result = token_manager.get_nft_token_ids(wallet_address, contract)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)

@bp.route('/nft/transfer', methods=['POST'])
def transfer_nft():
    data = request.get_json()
    if not data or not all(k in data for k in ['sender_address', 'recipient_address', 'token_id', 'private_key', 'nft_address']):
        return jsonify({"error": "Missing required fields"}), 400
    
    contract, nft_info = token_manager.load_erc721_contract(data['nft_address'])
    if not contract:
        return jsonify(nft_info), 400
    
    result = token_manager.send_nft(
        data['sender_address'],
        contract,
        data['recipient_address'],
        data['token_id'],
        data['private_key']
    )
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)

@bp.route('/native/transfer', methods=['POST'])
def transfer_native():
    data = request.get_json()
    if not data or not all(k in data for k in ['sender_address', 'recipient_address', 'amount', 'private_key']):
        return jsonify({"error": "Missing required fields"}), 400
    
    result = token_manager.send_native_token(
        data['sender_address'],
        data['recipient_address'],
        data['amount'],
        data['private_key']
    )
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result) 