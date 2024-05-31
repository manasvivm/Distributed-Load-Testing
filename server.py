from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/ping', methods=['GET'])
def ping():
    return 'PONG'

@app.route('/metrics', methods=['GET'])
def metrics():
    # Implement your metrics logic here
    return jsonify({'requests_sent': 100, 'responses_received': 100})

if __name__ == '__main__':
    app.run(port=8080)