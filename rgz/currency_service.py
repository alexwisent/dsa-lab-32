from flask import Flask, request, jsonify

app = Flask(__name__)

# Статические курсы относительно рубля
CURRENCY_RATES = {
    "USD": 90.0,
    "EUR": 100.0
}


@app.route("/rate", methods=["GET"])
def rate():
    currency = request.args.get("currency")

    # Неизвестная валюта -> 400
    if not currency or currency not in CURRENCY_RATES:
        return jsonify({"message": "UNKNOWN CURRENCY"}), 400

    try:
        return jsonify({"rate": CURRENCY_RATES[currency]}), 200
    except Exception:
        return jsonify({"message": "UNEXPECTED ERROR"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)