from flask import Blueprint, jsonify, request
from .. import wallet_manager, chain_manager

bp = Blueprint('wallet', __name__)

@bp.route('/all', methods=['GET'])
def get_all_wallets():
    return jsonify(wallet_manager.get_all_wallets())

@bp.route('/add', methods=['POST'])
def add_wallet():
    data = request.get_json()
    if not data or 'name' not in data or 'address' not in data:
        return jsonify({"error": "Missing required fields"}), 400
    
    result = wallet_manager.add_wallet(data['name'], data['address'])
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)

@bp.route('/remove/<address>', methods=['DELETE'])
def remove_wallet(address):
    result = wallet_manager.remove_wallet(address)
    if "error" in result:
        return jsonify(result), 404
    return jsonify(result)

@bp.route('/balance/<address>', methods=['GET'])
def get_wallet_balance(address):
    result = wallet_manager.get_wallet_balance(chain_manager.web3, address)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result) 