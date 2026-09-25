import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash

app = Flask(__name__)

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)