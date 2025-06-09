from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from model import get_stock_prediction, get_chart
import os

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Flask backend is running!"

@app.route("/predict", methods=["GET"])
def predict():
    ticker = request.args.get("ticker", "").upper()
    try:
        prediction = get_stock_prediction(ticker)
        return jsonify(prediction)
    except Exception as e:
        return jsonify({"error": str(e)}), 404
    
@app.route("/create-chart", methods=["GET"])
def chart():
    ticker = request.args.get("ticker", "").upper()
    time_pd = request.args.get("period", "1mo")
    try:
        img_buf = get_chart(ticker, time_pd)
        return send_file(img_buf, mimetype='image/png')
    except Exception as e:
        return jsonify({"error": str(e)}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)