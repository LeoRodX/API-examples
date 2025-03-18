# Получает координаты МКС по Open-Notify-API и демонстрирует ее положение на Яндексе карте
import requests
import datetime
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import webbrowser
from collections import deque

# Настройки
API_KEY = 'ccbf550e-3043-4586-a5cc-85642cd8c4e8'  # Получите на https://developer.tech.yandex.ru/
HISTORY_SIZE = 3
positions_history = deque(maxlen=HISTORY_SIZE)


def get_iss_location():
    url = "http://api.open-notify.org/iss-now.json"
    try:
        response = requests.get(url)
        data = response.json()
        return {
            'lat': float(data['iss_position']['latitude']),
            'lon': float(data['iss_position']['longitude']),
            'timestamp': data['timestamp']
        }
    except Exception as e:
        print(f"Ошибка получения данных МКС: {e}")
        return None


def generate_map(api_key, positions):
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Траектория МКС</title>
        <script src="https://api-maps.yandex.ru/2.1/?apikey={api_key}&lang=ru_RU"></script>
        <style>
            #map {{ width: 100%; height: 600px; }}
        </style>
    </head>
    <body>
        <div id="map"></div>
        <script>
            ymaps.ready(init);

            function init() {{
                var map = new ymaps.Map('map', {{
                    center: [0, 0],
                    zoom: 2
                }});

                {generate_marks_js(positions)}
            }}
        </script>
    </body>
    </html>
    '''
    with open('iss_map.html', 'w', encoding='utf-8') as f:
        f.write(html)
    webbrowser.open('iss_map.html')


def generate_marks_js(positions):
    js_code = ''
    colors = ['#FF0000', '#00FF00', '#0000FF']  # Цвета для разных позиций
    for i, pos in enumerate(positions):
        js_code += f'''
        var placemark{i} = new ymaps.Placemark([{pos['lat']}, {pos['lon']}], {{
            hintContent: 'МКС {i + 1}',
            balloonContent: 'Время: {pos['time']}<br>Широта: {pos['lat']:.2f}<br>Долгота: {pos['lon']:.2f}'
        }}, {{
            preset: 'islands#{colors[i]}Icon',
            iconColor: '{colors[i]}'
        }});
        map.geoObjects.add(placemark{i});
        '''

    if positions:
        js_code += f'map.setCenter([{positions[0]["lat"]}, {positions[0]["lon"]}], 3);'
    return js_code


def main():
    # Получаем текущую позицию
    current_pos = get_iss_location()
    if not current_pos:
        return

    # Добавляем в историю
    positions_history.appendleft({
        'lat': current_pos['lat'],
        'lon': current_pos['lon'],
        'time': datetime.datetime.fromtimestamp(current_pos['timestamp']).strftime(
            '%Y-%m-%d %H:%M:%S')
    })

    # Генерируем карту
    generate_map(API_KEY, list(positions_history))

    print(f"Текущая позиция МКС сохранена. Всего позиций в истории: {len(positions_history)}")


if __name__ == "__main__":
    main()