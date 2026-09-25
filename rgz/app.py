import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

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

    # Таблица пользователей
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            login VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL
        )
    """)

    # Таблица операций (с учётом варианта 5)
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