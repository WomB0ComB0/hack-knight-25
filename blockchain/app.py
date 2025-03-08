from flask import Flask, jsonify, request
from uuid import uuid4
from blockchain import Blockchain, MINING_REWARD, MINING_SENDER

app = Flask(__name__)

blockchain = Blockchain()
node_identifier = str(uuid4()).replace('-', '')

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Blockchain API is running',
        'status': 'success'
    }), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    required_fields = ['sender', 'recipient', 'amount', 'signature']
    if not all(field in values for field in required_fields):
        return jsonify({'error': 'Missing transaction details'}), 400

    transaction_result = blockchain.submit_transaction(
        values['sender'],
        values['recipient'],
        values['amount'],
        values['signature']
    )

    if transaction_result:
        return jsonify({'message': f'Transaction will be added to Block {transaction_result}'}), 201
    else:
        return jsonify({'error': 'Invalid Transaction'}), 406

@app.route('/transactions/new', methods=['GET'])
def transaction_instructions():
    return jsonify({
        'instructions': 'Send a POST request to this URL with sender, recipient, amount, and signature in JSON format.'
    }), 200

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

@app.route('/mine', methods=['GET'])
def mine():
    nonce = blockchain.proof_of_work()
    blockchain.submit_transaction(sender_address=MINING_SENDER,
                                  recipient_address=node_identifier,
                                  amount=MINING_REWARD)

    last_block = blockchain.chain[-1]
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(nonce, previous_hash)

    response = {
        'message': 'New Block Forged',
        'block_number': block['index'],
        'transactions': block['transactions'],
        'nonce': block['nonce'],
        'previous_hash': block['previous_hash']
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()
    nodes = values.get('nodes')

    if nodes is None:
        return jsonify({'error': 'Please supply a valid list of nodes'}), 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes)
    }
    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200

@app.route('/nodes/get', methods=['GET'])
def get_nodes():
    response = {
        'nodes': list(blockchain.nodes)
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
