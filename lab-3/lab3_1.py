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
            return jsonify({'error': 'Отсутствует параметр запроса: param'}), 400    # ошибка

        param = float(param)    # преобразуем строку в число
        random_number = random.uniform(1, 100)  # uniform - генерируем случайное число из диапазона в формате float
        result = random_number * param  # умножаем случайное число на param

        return jsonify({    # возвращаем ответ в формате JSON
            'result': result,   # результат вычисления
            'operation': 'mul'  # умножение
        })
    except ValueError:  # если param нельзя преобразовать в число
        return jsonify({'error': 'параметр должен быть числом'}), 400    # ошибка


# 2) Реализовать POST эндпоинт /number/, который принимает в теле 
# запроса JSON с полем jsonParam. Вернуть сгенерировать рандомно 
# число, умноженное на то, что пришло в JSON и рандомно выбрать операцию. 
@app.route('/number/', methods=['POST'])
def post_number():
    """
    POST эндпоинт:
    Принимает JSON с полем 'jsonParam'.
    Возвращает случайное число, умноженное на jsonParam,
    и случайную операцию (операция не влияет на результат).
    """
    data = request.get_json()   # получаем JSON из тела запроса

    if data is None or 'jsonParam' not in data: # проверяем наличие нужного поля
        return jsonify({'error': 'Отсутствует или некорректный JSON. Требуется поле jsonParam'}), 400

    try:
        value = float(data['jsonParam'])  # data['jsonParam'] - обращение к занчению по ключу и преобразуем в float
        random_number = random.uniform(1, 100)  # uniform - генерируем случайное число из диапазона в формате float
        result = random_number * value  # умножаем то что пишло на вход и рандомное число

        operation = random.choice(['sum', 'sub', 'mul', 'div']) # выбор случайной операции

        response = {    # формируем ответ
            'random_number': random_number, # случайное число
            'input_value': value,   # входное значение
            'result': result,   # результат
            'operation': operation  # рандомно выбранная операция
        }

        return jsonify(response)    # возвращаем JSON

    except ValueError:
        return jsonify({'error': 'jsonParam должен быть числом'}), 400


# 3) Реализовать DELETE эндпоинт /number/, 
# в ответе сгенерировать число и рандомную операцию.
@app.route('/number/', methods=['DELETE'])
def delete_number():
    """
    DELETE эндпоинт:
    Генерирует одно случайное число и случайную операцию.
    """

    random_number = random.uniform(1, 100)  # uniform - генерируем случайное число из диапазона в формате float
    operation = random.choice(['sum', 'sub', 'mul', 'div']) # случайная операция

    response = {    # формируем JSON-ответ
        'number': random_number,
        'operation': operation
    }

    return jsonify(response)    # возвращаем ответ


if __name__ == '__main__':  # точка входа в программу
    app.run(debug=True)  # запускаем сервер в режиме отладки