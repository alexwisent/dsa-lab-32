from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

# Подключение к базе
def db():
    return psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="admin",
        host="localhost",
        port="5432"
    )



@app.get("/convert")    # конвертация валюты
def convert():
    currency = request.args.get("currency_name", "").strip().upper()    # валюта
    amount_str = request.args.get("amount")     # сумма для конвертации

    if not currency or not amount_str:  # проверка параметров и превращаем сумму для конвертации в число
        return jsonify({"error": "Нужны currency_name и amount"}), 400
    try:
        amount = float(amount_str)
    except:
        return jsonify({"error": "amount должен быть числом"}), 400

    with db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT rate FROM currencies WHERE currency_name = %s", (currency,))    # получаем курс указанной валюты
        row = cur.fetchone()

        if not row: # проверяем что валюта есть в БД
            return jsonify({"error": "Валюты нет в БД"}), 404

        rate = float(row[0])    # Получаем курс из результата SQL-запроса
        converted = amount * rate   # конвертируем

    # Возвращаем JSON с результатом
    return jsonify({
        "currency": currency,
        "amount": amount,
        "rate": rate,
        "converted_to_rub": round(converted, 2)
    }), 200



@app.get("/currencies")     # вывод всех валют из currencies
def get_currencies():
    with db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, currency_name, rate FROM currencies ORDER BY currency_name")    # Получаем id, название валюты и её курс.
        rows = cur.fetchall()

    # Формируем список всех валют
    currencies = [
        {"id": row[0], "currency_name": row[1], "rate": float(row[2])}
        for row in rows
    ]

    return jsonify(currencies), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)