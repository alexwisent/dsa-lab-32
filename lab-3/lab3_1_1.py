# 1) Реализовать GET эндпоинт /number/, 
# который принимает параметр запроса – param с числом. 
# Вернуть рандомно сгенерированное число, 
# умноженное на значение из параметра в формате JSON. 

# 2) Реализовать POST эндпоинт /number/, который принимает в теле 
# запроса JSON с полем jsonParam.Вернуть сгенерировать рандомно 
# число, умноженное на то, что пришло в JSON и рандомно выбрать операцию. 

# 3) Реализовать DELETE эндпоинт /number/, 
# в ответе сгенерировать число и рандомную операцию.


import random
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/number/', methods=['GET'])
def get_number():
    """
    GET эндпоинт:
    Принимает query-параметр 'param' (число).
    Возвращает случайное число, умноженное на param.
    """
    try:
        param = request.args.get('param')
        if param is None:
            return jsonify({'error': 'Missing query parameter: param'}), 400

        param = float(param)
        random_number = random.uniform(1, 100)  # случайное число от 1 до 100
        result = random_number * param

        return jsonify({
            'result': result,
            'operation': 'mul'  # умножение
        })
    except ValueError:
        return jsonify({'error': 'param must be a number'}), 400


@app.route('/number/', methods=['POST'])
def post_number():
    """
    POST эндпоинт:
    Принимает JSON с полем 'jsonParam'.
    Возвращает случайное число, умноженное на jsonParam,
    и случайную операцию.
    """
    data = request.get_json()
    if data is None or 'jsonParam' not in data:
        return jsonify({'error': 'Missing or invalid JSON. Required field: jsonParam'}), 400

    try:
        value = float(data['jsonParam'])
        random_number = random.uniform(1, 100)
        result = random_number * value

        # Случайный выбор операции
        operation = random.choice(['sum', 'sub', 'mul', 'div'])

        # Для операций, отличных от умножения, пересчитываем результат
        if operation == 'sum':
            result = random_number + value
        elif operation == 'sub':
            result = random_number - value
        elif operation == 'div':
            if value == 0:
                result = None
            else:
                result = random_number / value
        # mul оставляем как есть

        response = {
            'random_number': random_number,
            'input_value': value,
            'result': result if result is not None else 'division by zero',
            'operation': operation
        }
        return jsonify(response)

    except ValueError:
        return jsonify({'error': 'jsonParam must be a number'}), 400


@app.route('/number/', methods=['DELETE'])
def delete_number():
    """
    DELETE эндпоинт:
    Генерирует случайное число и случайную операцию.
    """
    random_number = random.uniform(1, 100)
    second_number = random.uniform(1, 50)
    operation = random.choice(['sum', 'sub', 'mul', 'div'])

    if operation == 'sum':
        result = random_number + second_number
    elif operation == 'sub':
        result = random_number - second_number
    elif operation == 'mul':
        result = random_number * second_number
    elif operation == 'div':
        if second_number == 0:
            result = None
        else:
            result = random_number / second_number

    response = {
        'first_number': random_number,
        'second_number': second_number,
        'result': result if result is not None else 'division by zero',
        'operation': operation
    }
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)