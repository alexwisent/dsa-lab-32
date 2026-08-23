from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['SECRET_KEY'] = 'super-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# 2. Модель User
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)   # 200 лучше, чем 100 (хеш длинный)
    name = db.Column(db.String(1000), nullable=False)

    def __repr__(self):
        return f'<User {self.email}>'


# Обязательная функция для flask-login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Создание таблицы (один раз)
with app.app_context():
    db.create_all()

