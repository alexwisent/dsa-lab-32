from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['SECRET_KEY'] = 'super-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)    # создаём объект для работы с БД

login_manager = LoginManager()  # менеджер авторизации
login_manager.login_view = 'login'
login_manager.init_app(app)

# 2. Создать модель для работы с пользователями User на основе базового класса UserMixin 
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(1000), nullable=False)

    def __repr__(self): # вывод email
        return f'<User {self.email}>'


# Функция load_user обязательна для flask-login, чтобы при каждом запросе по сохранённому 
# в сессии id находить пользователя в базе и делать его доступным через current_user.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Создание таблицы
with app.app_context():
    db.create_all()


# 3. Создать endpoint для перехода на корневую страницу GET /. 
@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html')
    else:
        return redirect(url_for('login'))

