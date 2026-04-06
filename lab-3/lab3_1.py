import random   # модуль для генерации случайных чисел
from flask import Flask, request, jsonify   # импорт компонентов Flask

app = Flask(__name__)   # создаём экземпляр приложения Flask

# 1) Реализовать GET эндпоинт /number/, 
# который принимает параметр запроса – param с числом. 
# Вернуть рандомно сгенерированное число, 
# умноженное на значение из параметра в формате JSON.
@app.route('/number/', methods=['GET']) # объявляем GET эндпоинт /number/
def get_number():
    """
    GET эндпоинт:
    Принимает query-параметр 'param' (число).
    Возвращает случайное число, умноженное на param.
    """
    try:
        param = request.args.get('param')   # получаем параметр из URL (?param=...)
        if param is None:   # если параметр не передан
            return jsonify({'error': 'Missing query parameter: param'}), 400    # ошибка

        param = float(param)    # преобразуем строку в число
        random_number = random.uniform(1, 100)  # генерируем случайное число от 1 до 100
        result = random_number * param  # умножаем случайное число на param

        return jsonify({    # возвращаем ответ в формате JSON
            'result': result,   # результат вычисления
            'operation': 'mul'  # умножение
        })
    except ValueError:  # если param нельзя преобразовать в число
        return jsonify({'error': 'param must be a number'}), 400    # ошибка


# 2) Реализовать POST эндпоинт /number/, который принимает в теле 
# запроса JSON с полем jsonParam.Вернуть сгенерировать рандомно 
# число, умноженное на то, что пришло в JSON и рандомно выбрать операцию. 
@app.route('/number/', methods=['POST'])    # объявляем POST эндпоинт /number/
def post_number():
    """
    POST эндпоинт:
    Принимает JSON с полем 'jsonParam'.
    Возвращает случайное число, умноженное на jsonParam,
    и случайную операцию.
    """
    data = request.get_json()   # получаем JSON из тела запроса
    if data is None or 'jsonParam' not in data: # проверяем наличие нужного поля
        return jsonify({'error': 'Missing or invalid JSON. Required field: jsonParam'}), 400

    try:
        value = float(data['jsonParam'])    # преобразуем значение в число
        random_number = random.uniform(1, 100)  # генерируем случайное число
        result = random_number * value  # изначально считаем как умножение

        # Случайный выбор операции
        operation = random.choice(['sum', 'sub', 'mul', 'div'])

        # Для операций, отличных от умножения, пересчитываем результат
        if operation == 'sum':  # сложение
            result = random_number + value
        elif operation == 'sub':    # вычитание
            result = random_number - value
        elif operation == 'div':    # деление
            if value == 0:  # проверка деления на 0
                result = None
            else:
                result = random_number / value
        # если mul(умножение), то оставляем как есть

        response = {    # формируем ответ
            'random_number': random_number, # случайное число
            'input_value': value,   # входное значение
            'result': result if result is not None else 'division by zero', # если деление на 0 — текст
            'operation': operation  # выбранная операция
        }
        return jsonify(response)    # возвращаем JSON

    except ValueError:  # если jsonParam не число
        return jsonify({'error': 'jsonParam must be a number'}), 400


# 3) Реализовать DELETE эндпоинт /number/, 
# в ответе сгенерировать число и рандомную операцию.
@app.route('/number/', methods=['DELETE'])  # объявляем DELETE эндпоинт
def delete_number():
    """
    DELETE эндпоинт:
    Генерирует случайное число и случайную операцию.
    """
    random_number = random.uniform(1, 100)  # первое случайное число
    second_number = random.uniform(1, 50)   # второе случайное число
    operation = random.choice(['sum', 'sub', 'mul', 'div']) # случайная операция

    if operation == 'sum':  # сложение
        result = random_number + second_number
    elif operation == 'sub':    # вычитание
        result = random_number - second_number
    elif operation == 'mul':    # умножение
        result = random_number * second_number
    elif operation == 'div':    # деление
        if second_number == 0:  # защита от деления на 0
            result = None
        else:
            result = random_number / second_number

    response = {    # формируем JSON-ответ
        'first_number': random_number,  # первое число
        'second_number': second_number,  # второе число
        'result': result if result is not None else 'division by zero',
        'operation': operation  # операция
    }
    return jsonify(response)    # возвращаем ответ


if __name__ == '__main__':  # точка входа в программу
    app.run(debug=True)  # запускаем сервер в режиме отладки