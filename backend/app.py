from flask import Flask, jsonify, request
from flask_cors import CORS
from routes import api_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def index():
    return jsonify({'message': 'PCL Get Backend API'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)