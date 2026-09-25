import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import requests

app = Flask(__name__)
app.secret_key = "super-secret-key"

# Flask-Login
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


# Класс пользователя для Flask-Login
class User(UserMixin):
    def __init__(self, id, login):
        self.id = id
        self.login = login


@login_manager.user_loader
def load_user(user_id):
    with db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, login FROM users WHERE id = %s", (user_id,))
        row = cur.fetchone()
        if row:
            return User(row[0], row[1])
    return None


# 1.1 Подключение к БД
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


# Создаём таблицы при запуске
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

    # Таблица operations (с payment_method — Вариант 5)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS operations (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            sum NUMERIC(12, 2) NOT NULL CHECK (sum > 0),
            chat_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
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


# Главная страница
@app.route("/")
def index():
    if current_user.is_authenticated:
        return render_template("index.html")
    return redirect(url_for("login"))


# ---------------- 1.2 РЕГИСТРАЦИЯ ----------------
# По заданию: POST /reg принимает JSON с логином и паролем.
# Но чтобы вы могли пользоваться сайтом, добавлена и HTML-форма.
@app.route("/reg", methods=["GET", "POST"])
def reg():
    if request.method == "POST":
        # Если пришёл JSON — работаем как требует задание
        if request.is_json:
            data = request.get_json()
            login = data.get("login")
            password = data.get("password")
        else:
            # Если пришла обычная форма с сайта
            login = request.form.get("login")
            password = request.form.get("password")

        if not login or not password:
            if request.is_json:
                return jsonify({"error": "login and password required"}), 400
            flash("Заполните все поля", "error")
            return render_template("reg.html")

        try:
            with db() as conn:
                cur = conn.cursor()
                # Проверяем, что логин свободен
                cur.execute("SELECT id FROM users WHERE login = %s", (login,))
                if cur.fetchone() is not None:
                    if request.is_json:
                        return jsonify({"error": "user already exists"}), 400
                    flash("Пользователь с таким логином уже существует", "error")
                    return render_template("reg.html")

                # Сохраняем логин и хеш пароля
                password_hash = generate_password_hash(password)
                cur.execute(
                    "INSERT INTO users (login, password_hash) VALUES (%s, %s)",
                    (login, password_hash)
                )
                conn.commit()

            # Ответ по заданию: 200 OK
            if request.is_json:
                return jsonify({"status": "OK"}), 200

            flash("Регистрация прошла успешно. Теперь войдите.", "success")
            return redirect(url_for("login"))

        except Exception as e:
            print("Ошибка регистрации:", e)
            if request.is_json:
                return jsonify({"error": "internal server error"}), 500
            flash("Внутренняя ошибка сервера", "error")
            return render_template("reg.html")

    # GET — показываем форму регистрации
    return render_template("reg.html")


# ---------------- АВТОРИЗАЦИЯ ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_name = request.form.get("login")
        password = request.form.get("password")

        if not login_name or not password:
            flash("Заполните все поля", "error")
            return render_template("login.html")

        with db() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, login, password_hash FROM users WHERE login = %s",
                (login_name,)
            )
            row = cur.fetchone()

        if not row:
            flash("Пользователь не найден", "error")
            return render_template("login.html")

        if not check_password_hash(row[2], password):
            flash("Неверный пароль", "error")
            return render_template("login.html")

        user = User(row[0], row[1])
        login_user(user)
        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# ---------------- 1.3 ДОБАВЛЕНИЕ ОПЕРАЦИИ ----------------
# По заданию: POST /add_operation принимает JSON.
# Но также работает и HTML-форма, чтобы вы могли пользоваться сайтом.
@app.route("/add_operation", methods=["GET", "POST"])
@login_required
def add_operation():
    if request.method == "POST":
        # Поддержка JSON (по заданию)
        if request.is_json:
            data = request.get_json()
            type_operation = data.get("type_operation")
            sum_value = data.get("sum")
            date_value = data.get("date")
            payment_method = data.get("payment_method")
            user_id = data.get("user_id")
            # По заданию клиент присылает user_id, но мы проверяем,
            # что он совпадает с текущим авторизованным пользователем
            if user_id is not None and int(user_id) != int(current_user.id):
                return jsonify({"error": "user mismatch"}), 403
        else:
            type_operation = request.form.get("type_operation")
            sum_value = request.form.get("sum")
            date_value = request.form.get("date")
            payment_method = request.form.get("payment_method")

        # Валидация
        if not type_operation or not sum_value or not date_value:
            if request.is_json:
                return jsonify({"error": "missing fields"}), 400
            flash("Заполните все обязательные поля", "error")
            return render_template("add_operation.html")

        # Логика варианта 5:
        # ДОХОД -> payment_method = NULL
        # РАСХОД -> payment_method обязательно НАЛИЧНЫЕ или КАРТА
        if type_operation == "ДОХОД":
            payment_method = None
        elif type_operation == "РАСХОД":
            if payment_method not in ("НАЛИЧНЫЕ", "КАРТА"):
                if request.is_json:
                    return jsonify({"error": "invalid payment method"}), 400
                flash("Для расхода выберите способ оплаты", "error")
                return render_template("add_operation.html")
        else:
            if request.is_json:
                return jsonify({"error": "invalid type_operation"}), 400
            flash("Неверный тип операции", "error")
            return render_template("add_operation.html")

        try:
            with db() as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO operations
                        (date, sum, chat_id, type_operation, payment_method)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    date_value,
                    sum_value,
                    current_user.id,
                    type_operation,
                    payment_method
                ))
                conn.commit()

            if request.is_json:
                return jsonify({"status": "OK"}), 200

            flash("Операция добавлена", "success")
            return redirect(url_for("operations"))

        except Exception as e:
            print("Ошибка добавления операции:", e)
            if request.is_json:
                return jsonify({"error": "internal server error"}), 500
            flash("Внутренняя ошибка сервера", "error")
            return render_template("add_operation.html")

    # GET — показываем форму
    return render_template("add_operation.html")


# ---------------- 1.4 ПРОСМОТР ОПЕРАЦИЙ ----------------
@app.route("/operations", methods=["GET"])
@login_required
def operations():
    currency = request.args.get("currency", "RUB")
    rate = 1.0

    if currency in ("USD", "EUR"):
        try:
            resp = requests.get(
                f"http://localhost:5001/rate?currency={currency}",
                timeout=3
            )
            if resp.status_code == 200:
                rate = float(resp.json().get("rate", 1.0))
            else:
                rate = 1.0
        except Exception as e:
            print("Ошибка внешнего сервиса:", e)
            rate = 1.0

    with db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT date, sum, type_operation, payment_method
            FROM operations
            WHERE chat_id = %s
            ORDER BY date DESC
        """, (current_user.id,))
        rows = cur.fetchall()

    result = []
    for r in rows:
        orig_sum = float(r[1])
        converted = round(orig_sum / rate, 2)

        type_op = (r[2] or "").lower()          # "доход" / "расход"
        payment = (r[3] or "").lower() if r[3] else "—"

        # Для расхода показываем сумму со знаком минус
        if type_op == "расход":
            display_sum = -converted
        else:
            display_sum = converted

        result.append({
            "date": r[0],
            "sum": display_sum,
            "type_operation": type_op,
            "payment_method": payment
        })

    return render_template(
        "operations.html",
        operations=result,
        currency=currency
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)