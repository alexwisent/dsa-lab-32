import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from flask import Flask, request, render_template, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

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

    # Таблица operations 
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


# 1.2. Регистрация
# 1.2.1. Клиент отправляется запрос /reg с телом в JSON формате. Тело запроса должно содержать логин и пароль.
@app.route("/reg", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Поддерживаем JSON (по заданию) и форму (для Jinja)
        if request.is_json:
            data = request.get_json()
            login = data.get("login", "").strip() if data else ""
            password = data.get("password", "") if data else ""
        else:
            login = request.form.get("login", "").strip()
            password = request.form.get("password", "")

        if not login or not password:
            if request.is_json:
                return jsonify({"error": "Нужны login и password"}), 400
            flash("Заполните все поля", "error")
            return render_template("register.html")

        # Хешируем пароль
        password_hash = generate_password_hash(password)

        try:
            with db() as conn:
                cur = conn.cursor()

                # 1.2.2. Backend проверяет, что пользователь не зарегистрирован
                cur.execute("SELECT 1 FROM users WHERE login = %s", (login,))
                if cur.fetchone():
                    if request.is_json:
                        return jsonify({"error": "Пользователь уже зарегистрирован"}), 409
                    flash("Пользователь уже зарегистрирован", "error")
                    return render_template("register.html")

                # 1.2.3. Backend сохраняет логин и пароль (в виде хэша) в БД
                cur.execute(
                    "INSERT INTO users (login, password_hash) VALUES (%s, %s)",
                    (login, password_hash)
                )
                conn.commit()

            # 1.2.4. Успешный ответ
            if request.is_json:
                return jsonify({"message": "Регистрация успешна"}), 200

            flash("Регистрация успешна! Теперь войдите.", "success")
            return redirect(url_for("login"))

        except Exception:
            # 1.2.5. Любая ошибка: 500
            if request.is_json:
                return jsonify({"error": "Внутренняя ошибка сервера"}), 500
            flash("Внутренняя ошибка сервера", "error")
            return render_template("register.html")

    return render_template("register.html")


# Авторизация
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login = request.form.get("login", "").strip()
        password = request.form.get("password", "")

        if not login or not password:
            flash("Заполните все поля", "error")
            return render_template("login.html")

        with db() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, login, password_hash FROM users WHERE login = %s",
                (login,)
            )
            user_data = cur.fetchone()

        if not user_data:
            flash("Неверный логин или пароль", "error")
            return render_template("login.html")

        user_id, user_login, password_hash = user_data

        if not check_password_hash(password_hash, password):
            flash("Неверный логин или пароль", "error")
            return render_template("login.html")

        user = User(user_id, user_login)
        login_user(user)
        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))





if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)