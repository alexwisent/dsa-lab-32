import requests
import random

# Базовый URL API (локальный сервер Flask)
BASE_URL = "http://127.0.0.1:5000"


# =========================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =========================

def get_random():
    """Генерация случайного целого числа от 1 до 10."""
    return random.randint(1, 10)    # randint - генерит случайное целое число из диапазона 


def apply_operation(a, op, b):
    """
    Выполнение арифметической операции между двумя числами.

    :param a: первое число
    :param op: операция (sum, sub, mul, div)
    :param b: второе число
    :return: результат вычисления
    """
    if op == "sum":
        return a + b
    if op == "sub":
        return a - b
    if op == "mul":
        return a * b
    if op == "div":
        return a / b if b != 0 else 0

    # Если пришла неизвестная операция — ошибка
    raise ValueError(f"Неизвестная операция: {op}")


# =========================
# 1) GET /number
# =========================

# Генерация случайного параметра для GET запроса
param = get_random()

# Отправка GET запроса с query-параметром
res_get = requests.get(
    f"{BASE_URL}/number/",
    params={"param": param}
)

# Получение JSON-ответа
data_get = res_get.json()

print("GET ответ:", data_get)

# Извлекаем результат и операцию из ответа
a = float(data_get["result"])
op1 = data_get["operation"]


# =========================
# 2) POST /number
# =========================

# Генерация случайного значения для JSON тела
json_param = get_random()

# Отправка POST запроса
post_response = requests.post(
    f"{BASE_URL}/number/",
    json={"jsonParam": json_param}
)

# Получение ответа
data_post = post_response.json()

print("POST ответ:", data_post)

# Извлечение данных
b = float(data_post["result"])
op2 = data_post["operation"]


# =========================
# 3) DELETE /number
# =========================

# Отправка DELETE запроса
res_delete = requests.delete(f"{BASE_URL}/number/")

# Получение ответа
data_delete = res_delete.json()

print("DELETE ответ:", data_delete)

# Извлекаем результат и операцию
c = float(data_delete["number"])
op3 = data_delete["operation"]


# =========================
# 4) ФОРМИРОВАНИЕ И ВЫЧИСЛЕНИЕ ВЫРАЖЕНИЯ
# =========================

# Последовательное выполнение операций:
# сначала GET результат → POST → DELETE

result = apply_operation(a, op1, b)
result = apply_operation(result, op2, c)

# Приведение результата к целому числу
final_result = int(result)

print("\nОкончательные результат:", final_result)