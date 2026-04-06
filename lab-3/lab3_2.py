

import random
import requests


BASE_URL = "http://127.0.0.1:5000/number/"


def apply_operation(a, b, operation):
    """Выполнение операции"""
    if operation == "sum":
        return a + b
    if operation == "sub":
        return a - b
    if operation == "mul":
        return a * b
    if operation == "div":
        return a / b if b != 0 else 0


# -------- 1. GET --------
param = random.randint(1, 10)

get_response = requests.get(BASE_URL, params={"param": param})
get_data = get_response.json()

print("GET response:", get_data)

result_1 = get_data["result"]


# -------- 2. POST --------
json_param = random.randint(1, 10)

post_response = requests.post(
    BASE_URL,
    json={"jsonParam": json_param}
)
post_data = post_response.json()

print("POST response:", post_data)

result_2 = post_data["result"]


# -------- 3. DELETE --------
delete_response = requests.delete(BASE_URL)
delete_data = delete_response.json()

print("DELETE response:", delete_data)

# для DELETE у тебя 2 числа → нужно применить операцию
result_3 = apply_operation(
    delete_data["first_number"],
    delete_data["second_number"],
    delete_data["operation"]
)


# -------- 4. Итоговое выражение --------
# выполняем последовательно: ((result_1 OP result_2) OP result_3)

# сначала операция из POST
intermediate = apply_operation(result_1, result_2, post_data["operation"])

# затем операция из DELETE
final_result = apply_operation(intermediate, result_3, delete_data["operation"])

# приводим к int
final_result_int = int(final_result)

print("\nFinal result:", final_result_int)