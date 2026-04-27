# инструкция как запустить тест для lab-3\lab3_1.py:
# python lab3_1.py	# это запуск сервера 

# оставить этот терминал работать и открыть новый 

# cd lab-3	# перейти в правильную папку

# python lab3_1_test_all.py	# это запуск тестов 


import requests

BASE_URL = "http://127.0.0.1:5000/number/"

print("=" * 50)
print("ТЕСТИРОВАНИЕ API")
print("=" * 50)

# 1. GET эндпоинт
print("\n1. GET запрос:")
param = 7
response = requests.get(BASE_URL, params={"param": param})
data = response.json()
print(f"   URL: {BASE_URL}?param={param}")
print(f"   Ответ: {data}")
print(f"   Результат: {data['result']} (операция: {data['operation']})")

# 2. POST эндпоинт
print("\n2. POST запрос:")
json_value = 5
response = requests.post(BASE_URL, json={"jsonParam": json_value})
data = response.json()
print(f"   Тело запроса: {{'jsonParam': {json_value}}}")
print(f"   Ответ: {data}")
print(f"   Результат: {data['result']} (операция: {data['operation']})")

# 3. DELETE эндпоинт
print("\n3. DELETE запрос:")
response = requests.delete(BASE_URL)
data = response.json()
print(f"   Ответ: {data}")
print(f"   Результат: {data['result']} (операция: {data['operation']})")

print("\n" + "=" * 50)
print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
print("=" * 50)