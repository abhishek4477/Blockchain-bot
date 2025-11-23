from flask import Flask, jsonify
from flask_cors import CORS
from app.routes import chain_routes, wallet_routes, token_routes

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(chain_routes.bp, url_prefix='/api/chain')
app.register_blueprint(wallet_routes.bp, url_prefix='/api/wallet')
app.register_blueprint(token_routes.bp, url_prefix='/api/token')

@app.route('/')
def root():
    return jsonify({"message": "Welcome to EVM Transfer Bot API"})

if __name__ == '__main__':
    app.run(debug=True) 