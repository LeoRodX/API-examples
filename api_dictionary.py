# API отдачи значения словаря
# - Получить значение для слова "apple":http://localhost:5000/get_value/apple
# или curl http://localhost:5000/get_value/apple
# - Получить весь словарь: http://localhost:5000/get_all
# - Запрос несуществующего ключа:http://localhost:5000/get_value/dog
from flask import Flask, Response, jsonify, json

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # Отключаем экранирование Unicode

# Пример словаря с данными
sample_dict = {
    "apple": "яблоко",
    "car": "машина",
    "book": "книга",
    "computer": "компьютер"
}


@app.route('/get_value/<key>', methods=['GET'])
def get_value(key):
    value = sample_dict.get(key)
    if value:
        return Response(
            json.dumps({key: value}, ensure_ascii=False),
            mimetype='application/json; charset=utf-8'
        )
    return Response(
        json.dumps({"error": "Ключ не найден"}, ensure_ascii=False),
        mimetype='application/json; charset=utf-8'
    )


@app.route('/get_all', methods=['GET'])
def get_all():
    return Response(
        json.dumps(sample_dict, ensure_ascii=False),
        mimetype='application/json; charset=utf-8'
    )


if __name__ == '__main__':
    app.run(debug=True)