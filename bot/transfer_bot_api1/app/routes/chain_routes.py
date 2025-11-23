from flask import Blueprint, jsonify
from .. import chain_manager

bp = Blueprint('chain', __name__)

@bp.route('/current', methods=['GET'])
def get_current_chain():
    return jsonify(chain_manager.get_current_chain())

@bp.route('/change/<chain_name>', methods=['POST'])
def change_chain(chain_name):
    result = chain_manager.change_chain(chain_name)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result) 