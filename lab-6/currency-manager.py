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

# Создаём таблицу currencies при запуске, если ее еще нет
with db() as conn:
    conn.cursor().execute("""
        CREATE TABLE IF NOT EXISTS currencies (
            id SERIAL PRIMARY KEY,
            currency_name VARCHAR(10) UNIQUE NOT NULL,
            rate NUMERIC(15,6) NOT NULL
        )
    """)
    conn.commit()



@app.post("/load")  # добавление валюты
def load():
    data = request.get_json()
    name = data.get("currency_name", "").strip().upper()    # значение по ключу превращем в строку без пробелов, в верхний регистр
    rate = data.get("rate")     # получаем курс

    if not name or rate is None:    # проверка что данные передались
        return jsonify({"error": "Нужны currency_name и rate"}), 400
    
    if rate <= 0:   # проверка на корректность данных
        return jsonify({"error": "Курс должен быть положительным числом"}), 400
    
    with db() as conn:
        cur = conn.cursor()

        # 1. Проверка, что валюты ещё нет
        cur.execute("SELECT 1 FROM currencies WHERE currency_name = %s", (name,))
        if cur.fetchone():
            return jsonify({"error": "Валюта уже есть"}), 409

        # 2. Сохраняем валюту
        cur.execute("INSERT INTO currencies (currency_name, rate) VALUES (%s, %s)",
                    (name, float(rate)))
        conn.commit()

    # 3. Успешный ответ
    return jsonify({"message": "Валюта добавлена"}), 200



@app.post("/update_currency")   # изменение курса существующей валюты
def update_currency():
    data = request.get_json()
    name = data.get("currency_name", "").strip().upper()
    rate = data.get("rate")

    if not name or rate is None:    # проверка что данные передались
        return jsonify({"error": "Нужны currency_name и rate"}), 400
    rate = float(rate)

    if rate <= 0:   # проверка на корректность данных
        return jsonify({"error": "Курс должен быть положительным числом"}), 400
    
    with db() as conn:
        cur = conn.cursor()

        # 1. Проверка, что валюта существует
        cur.execute("SELECT 1 FROM currencies WHERE currency_name = %s", (name,))
        if not cur.fetchone():
            return jsonify({"error": "Валюты нет в БД"}), 404

        # 2. Обновляем курс
        cur.execute("UPDATE currencies SET rate = %s WHERE currency_name = %s",
                    (float(rate), name))
        conn.commit()

    # 3. Успешный ответ
    return jsonify({"message": "Курс обновлён"}), 200



@app.post("/delete")    # удаление существующей валюты
def delete_currency():
    data = request.get_json()
    name = data.get("currency_name", "").strip().upper()

    if not name:
        return jsonify({"error": "Нужно currency_name"}), 400

    with db() as conn:
        cur = conn.cursor()
        
        # 1. Проверяем, что валюта существует
        cur.execute("SELECT 1 FROM currencies WHERE currency_name = %s", (name,))
        if not cur.fetchone():
            return jsonify({"error": "Валюты нет в БД"}), 404

        # 2. Удаляем
        cur.execute("DELETE FROM currencies WHERE currency_name = %s", (name,))
        conn.commit()

    # 3. Успешный ответ
    return jsonify({"message": "Валюта удалена"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)