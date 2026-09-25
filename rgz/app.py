import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from flask import Flask, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "super-secret-key"   # нужен для работы сессий

# 1.1. Создание Базы Данных Posgres
# Подключение к базе
def db(database="finance_db"):
    return psycopg2.connect(
        dbname=database,
        user="postgres",
        password="admin",
        host="localhost",
        port="5432"
    )


# Создаём базу данных, если её ещё нет
conn = db("postgres")
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()
cur.execute("SELECT 1 FROM pg_database WHERE datname = 'finance_db'")
if cur.fetchone() is None:
    cur.execute("CREATE DATABASE finance_db")
    print("База данных finance_db создана")
else:
    print("База данных finance_db уже существует")
cur.close()
conn.close()


# Создаём таблицы при запуске, если их ещё нет
with db() as conn:
    cur = conn.cursor()

    # Таблица users
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            login VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL
        )
    """)

    # Таблица operations 
    cur.execute("""
        CREATE TABLE IF NOT EXISTS operations (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            sum NUMERIC(12, 2) NOT NULL
                CHECK (sum > 0),
            chat_id INTEGER NOT NULL
                REFERENCES users(id) ON DELETE CASCADE,
            type_operation VARCHAR(10) NOT NULL
                CHECK (type_operation IN ('ДОХОД', 'РАСХОД')),
            payment_method VARCHAR(20)
                CHECK (
                    payment_method IN ('НАЛИЧНЫЕ', 'КАРТА')
                    OR payment_method IS NULL
                ),
            CHECK (
                (type_operation = 'ДОХОД' AND payment_method IS NULL)
                OR
                (type_operation = 'РАСХОД' AND payment_method IS NOT NULL)
            )
        )
    """)

    conn.commit()
    print("Таблицы users и operations готовы")


# 1.2.1. Клиент отправляется запрос /reg с телом в JSON формате. Тело запроса должно содержать логин и пароль.
@app.post("/reg")
def register():
    try:
        data = request.get_json()

        # Проверяем, что пришли поля login и password
        if not data or "login" not in data or "password" not in data:
            return jsonify({"error": "Нужны login и password"}), 400

        login = data["login"].strip()
        password = data["password"]

        if not login or not password:
            return jsonify({"error": "login и password не могут быть пустыми"}), 400

        # Хешируем пароль
        password_hash = generate_password_hash(password)

        with db() as conn:
            cur = conn.cursor()

            # 1.2.2. Backend проверяет, что пользователь не зарегистрирован
            cur.execute("SELECT 1 FROM users WHERE login = %s", (login,))
            if cur.fetchone():
                return jsonify({"error": "Пользователь уже зарегистрирован"}), 409

            # 1.2.3. Backend сохраняет логин и пароль (в виде хэша) в БД
            cur.execute(
                """
                INSERT INTO users (login, password_hash)
                VALUES (%s, %s)
                """,
                (login, password_hash)
            )
            conn.commit()

        # 1.2.4. Успешный ответ
        return jsonify({"message": "Регистрация успешна"}), 200

    except Exception:
        # 1.2.5. Любая ошибка: 500
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500


# Авторизация
@app.post("/login")
def login():
    try:
        data = request.get_json()

        if not data or "login" not in data or "password" not in data:
            return jsonify({"error": "Нужны login и password"}), 400

        login = data["login"].strip()
        password = data["password"]

        with db() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, password_hash FROM users WHERE login = %s",
                (login,)
            )
            user = cur.fetchone()

        if not user:
            return jsonify({"error": "Неверный логин или пароль"}), 401

        user_id, password_hash = user

        if not check_password_hash(password_hash, password):
            return jsonify({"error": "Неверный логин или пароль"}), 401

        # Сохраняем id пользователя в сессии → он теперь авторизован
        session["user_id"] = user_id

        return jsonify({"message": "Авторизация успешна", "user_id": user_id}), 200

    except Exception:
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500


# 1. Клиент отправляет HTTP запрос /add_operation с телом в формате JSON. 
# Тело запрос содержит: тип операции (расход/доход), идентификатор пользователя, сумма операции в рублях, дата операции в рублях.
@app.post("/add_operation")
def add_operation():
    try:
        # 2. Backend проверяет что пользователь существует и авторизован
        if "user_id" not in session:
            return jsonify({"error": "Пользователь не авторизован"}), 401

        data = request.get_json()

        # Проверяем, что пришли нужные поля
        if not data:
            return jsonify({"error": "Тело запроса пустое"}), 400

        required = ["type_operation", "chat_id", "sum", "date"]
        for field in required:
            if field not in data:
                return jsonify({"error": f"Нужно поле {field}"}), 400

        type_operation = data["type_operation"].strip().upper()
        chat_id = data["chat_id"]
        sum_value = data["sum"]
        date = data["date"]

        # Проверка типа операции
        if type_operation not in ("ДОХОД", "РАСХОД"):
            return jsonify({"error": "type_operation должен быть ДОХОД или РАСХОД"}), 400

        # Проверка суммы
        try:
            sum_value = float(sum_value)
            if sum_value <= 0:
                return jsonify({"error": "sum должна быть положительным числом"}), 400
        except (TypeError, ValueError):
            return jsonify({"error": "sum должна быть числом"}), 400

        with db() as conn:
            cur = conn.cursor()

            # Проверяем, что пользователь существует
            cur.execute("SELECT 1 FROM users WHERE id = %s", (chat_id,))
            if not cur.fetchone():
                return jsonify({"error": "Пользователь не найден"}), 404

            # 3. Backend сохраняет полученную информацию в БД
            cur.execute(
                """
                INSERT INTO operations (date, sum, chat_id, type_operation)
                VALUES (%s, %s, %s, %s)
                """,
                (date, sum_value, chat_id, type_operation)
            )
            conn.commit()

        # 4. Backend формирует ответ 200 OK
        return jsonify({"message": "Операция добавлена"}), 200

    except Exception:
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)