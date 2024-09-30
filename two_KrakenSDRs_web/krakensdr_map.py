# GNU GENERAL PUBLIC LICENSE
# Version 3, 29 June 2007
#
# Copyright (C) 2024 Tarasenko Volodymyr hc158b@gmail.com https://x.com/VolodymyrTr
# This is the source code for KrakenSDR direction.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


# rm -rf venv
# python3 -m venv venv
#
# pip3 install -r requirements.txt



from flask import Flask, render_template, jsonify, request
import json
import math
import webbrowser
from threading import Timer, Thread
import asyncio
import websockets
import subprocess


app = Flask(__name__)

# Global variables for storing x_for_max_y
x_for_max_y_1 = None
x_for_max_y_2 = None

# WebSocket URLs for krakensdr_1 and krakensdr_2 are now loaded from the JSON files

# Load data from each JSON file
with open('data_krkn_1.json') as f1, open('data_krkn_2.json') as f2:
    data_krakensdr_1 = json.load(f1)
    data_krakensdr_2 = json.load(f2)

ws_url_1 = data_krakensdr_1['krakensdr_1']['ws_url']
ws_url_2 = data_krakensdr_2['krakensdr_2']['ws_url']

# Function to calculate the endpoint at a certain distance
def calculate_new_point(lat, lon, distance_km, bearing_deg):
    R = 6371  # Radius of the Earth in kilometers
    bearing = math.radians(bearing_deg)  # Convert bearing to radians

    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)

    new_lat_rad = math.asin(math.sin(lat_rad) * math.cos(distance_km / R) +
                            math.cos(lat_rad) * math.sin(distance_km / R) * math.cos(bearing))

    new_lon_rad = lon_rad + math.atan2(math.sin(bearing) * math.sin(distance_km / R) * math.cos(lat_rad),
                                       math.cos(distance_km / R) - math.sin(lat_rad) * math.sin(new_lat_rad))

    new_lat = math.degrees(new_lat_rad)
    new_lon = math.degrees(new_lon_rad)

    return new_lat, new_lon

# Route for the main page
@app.route('/')
def index():
    try:
        # Открываем и читаем freq_rqst_1.json
        with open('freq_rqst_1.json', 'r') as f:
            json_data = json.load(f)
            # Ищем значение частоты
            frequency_value = None
            for state in json_data['data']['state']:
                if state['id'] == 'daq_center_freq':
                    frequency_value = state['value']
                    break
        
        if frequency_value is None:
            frequency_value = 0  # Если значение не найдено, используем значение по умолчанию

        return render_template('index.html', frequency_value=frequency_value)

    except FileNotFoundError:
        return render_template('index.html', frequency_value=0)  # Значение по умолчанию, если файл не найден
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

# Route to get map data
@app.route('/get_map_data')
def get_map_data():
    global x_for_max_y_1, x_for_max_y_2

    try:
        # Load data from each JSON file
        with open('data_krkn_1.json') as f1, open('data_krkn_2.json') as f2:
            data_krakensdr_1 = json.load(f1)
            data_krakensdr_2 = json.load(f2)

        # Data for krakensdr_1
        krakensdr_1_data = data_krakensdr_1.get('krakensdr_1', {})
        start_coordinates_1 = krakensdr_1_data.get('start_coordinates', {})
        start_lat_1 = start_coordinates_1.get('latitude')
        start_lon_1 = start_coordinates_1.get('longitude')
        distance_km_1 = krakensdr_1_data.get('distance_km', 0)
        bearing_deg_1 = krakensdr_1_data.get('bearing_deg', 0)

        if x_for_max_y_1 is not None:
            x_for_max_y_modified_1 = (x_for_max_y_1 + bearing_deg_1) % 360
            end_lat_1, end_lon_1 = calculate_new_point(start_lat_1, start_lon_1, distance_km_1, x_for_max_y_modified_1)
        else:
            end_lat_1, end_lon_1 = start_lat_1, start_lon_1

        # Data for krakensdr_2
        krakensdr_2_data = data_krakensdr_2.get('krakensdr_2', {})
        start_coordinates_2 = krakensdr_2_data.get('start_coordinates', {})
        start_lat_2 = start_coordinates_2.get('latitude')
        start_lon_2 = start_coordinates_2.get('longitude')
        distance_km_2 = krakensdr_2_data.get('distance_km', 0)
        bearing_deg_2 = krakensdr_2_data.get('bearing_deg', 0)

        if x_for_max_y_2 is not None:
            x_for_max_y_modified_2 = (x_for_max_y_2 + bearing_deg_2) % 360
            end_lat_2, end_lon_2 = calculate_new_point(start_lat_2, start_lon_2, distance_km_2, x_for_max_y_modified_2)
        else:
            end_lat_2, end_lon_2 = start_lat_2, start_lon_2

        return jsonify({
            'krakensdr_1': {
                'start_lat': start_lat_1,
                'start_lon': start_lon_1,
                'end_lat': end_lat_1,
                'end_lon': end_lon_1
            },
            'krakensdr_2': {
                'start_lat': start_lat_2,
                'start_lon': start_lon_2,
                'end_lat': end_lat_2,
                'end_lon': end_lon_2
            }
        })

    except FileNotFoundError:
        return jsonify({'error': 'Data files not found'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route for updating marker coordinates
@app.route('/update_coordinates', methods=['POST'])
def update_coordinates():
    data = request.json  # Get data from the request
    krakensdr = data.get('krakensdr')  # Determine which KrakenSDR to update
    new_lat = data.get('latitude')
    new_lon = data.get('longitude')

    if not krakensdr or krakensdr not in ['krakensdr_1', 'krakensdr_2']:
        return jsonify({'error': 'Invalid KrakenSDR identifier'}), 400

    # Update the corresponding JSON file with new coordinates
    try:
        file_name = 'data_krkn_1.json' if krakensdr == 'krakensdr_1' else 'data_krkn_2.json'
        with open(file_name, 'r+') as f:
            json_data = json.load(f)
            
            # Update coordinates for the specified KrakenSDR
            json_data[krakensdr]['start_coordinates']['latitude'] = new_lat
            json_data[krakensdr]['start_coordinates']['longitude'] = new_lon
            
            f.seek(0)
            json.dump(json_data, f, indent=4)
            f.truncate()  # Remove the remnants of old data

        return jsonify({'status': 'success'})

    except FileNotFoundError:
        return jsonify({'error': f'{file_name} not found'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Новый маршрут для обновления bearing_deg для krakensdr_1 или krakensdr_2
@app.route('/update_bearing/<int:kraken_id>', methods=['POST'])
def update_bearing(kraken_id):
    data = request.json  # Получаем данные из запроса
    new_bearing_deg = data.get('bearing_deg')

    if kraken_id not in [1, 2]:
        return jsonify({'error': 'Invalid KrakenSDR identifier'}), 400

    # Выбираем правильный файл для обновления
    file_name = 'data_krkn_1.json' if kraken_id == 1 else 'data_krkn_2.json'
    krakensdr_key = 'krakensdr_1' if kraken_id == 1 else 'krakensdr_2'

    try:
        with open(file_name, 'r+') as f:
            json_data = json.load(f)
            
            # Обновляем значение bearing_deg
            json_data[krakensdr_key]['bearing_deg'] = new_bearing_deg
            
            f.seek(0)
            json.dump(json_data, f, indent=4)
            f.truncate()

        return jsonify({'status': 'success'})

    except FileNotFoundError:
        return jsonify({'error': f'{file_name} not found'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Новый маршрут для обновления значения частоты
@app.route('/update_frequency', methods=['POST'])
def update_frequency():
    data = request.json  # Получаем данные из запроса
    new_frequency_value = data.get('value')

    # Вы можете настроить путь к файлу, который нужно обновить
    file_name = 'freq_rqst_1.json'

    try:
        with open(file_name, 'r+') as f:
            json_data = json.load(f)
            
            # Обновляем значение частоты
            json_data['frequency'] = new_frequency_value
            
            f.seek(0)
            json.dump(json_data, f, indent=4)
            f.truncate()

        return jsonify({'status': 'success'})

    except FileNotFoundError:
        return jsonify({'error': f'{file_name} not found'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to get bearing value for KrakenSDR 1 or 2
@app.route('/get_bearing_value/<int:kraken_id>', methods=['GET'])
def get_bearing_value(kraken_id):
    if kraken_id not in [1, 2]:
        return jsonify({'error': 'Invalid KrakenSDR identifier'}), 400

    # Определение имени файла JSON
    file_name = 'data_krkn_1.json' if kraken_id == 1 else 'data_krkn_2.json'
    krakensdr_key = 'krakensdr_1' if kraken_id == 1 else 'krakensdr_2'

    try:
        with open(file_name, 'r') as f:
            json_data = json.load(f)
            bearing_deg = json_data[krakensdr_key].get('bearing_deg')
            return jsonify({'bearing_deg': bearing_deg})

    except FileNotFoundError:
        return jsonify({'error': f'{file_name} not found'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Маршрут для обновления частоты и запуска скрипта
@app.route('/update_frequency_and_run', methods=['POST'])
def update_frequency_and_run():
    data = request.json
    new_frequency = data.get('frequency')

    try:
        # Обновляем значения в freq_rqst_1.json
        with open('freq_rqst_1.json', 'r+') as f1:
            json_data_1 = json.load(f1)
            for state in json_data_1['data']['state']:
                if state['id'] == 'daq_center_freq':
                    state['value'] = new_frequency  # Обновляем значение частоты
            f1.seek(0)
            json.dump(json_data_1, f1, indent=4)
            f1.truncate()

        # Обновляем значения в freq_rqst_2.json
        with open('freq_rqst_2.json', 'r+') as f2:
            json_data_2 = json.load(f2)
            for state in json_data_2['data']['state']:
                if state['id'] == 'daq_center_freq':
                    state['value'] = new_frequency  # Обновляем значение частоты
            f2.seek(0)
            json.dump(json_data_2, f2, indent=4)
            f2.truncate()

        # Выполняем change_freq.py
        result = subprocess.run(['python3', 'change_freq.py'], capture_output=True, text=True)
        
        return jsonify({'status': 'success', 'script_output': result.stdout})

    except FileNotFoundError as e:
        return jsonify({'error': f'File not found: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Function to start update_data_periodically.py
def run_update_data_periodically():
    subprocess.run(['python3', 'update_data_periodically.py'])

# Function to update JSON for each KrakenSDR
def update_json(x_values, y_values, krakensdr):
    global x_for_max_y_1, x_for_max_y_2
    if x_values and y_values:
        max_y = max(y_values)
        if krakensdr == 'krakensdr_1':
            x_for_max_y_1 = x_values[y_values.index(max_y)]  # Update the global variable for krakensdr_1
        elif krakensdr == 'krakensdr_2':
            x_for_max_y_2 = x_values[y_values.index(max_y)]  # Update the global variable for krakensdr_2

        file_name = 'data_krkn_1.json' if krakensdr == 'krakensdr_1' else 'data_krkn_2.json'
        with open(file_name, 'r+') as f:
            data = json.load(f)
            
            if krakensdr == 'krakensdr_1':
                data['krakensdr_1']['angles_krakensdr'] = {
                    "max_y": max_y,
                    "x_for_max_y": x_for_max_y_1
                }
                print(f"krakensdr_1: x: {x_for_max_y_1}, y: {max_y}")
            elif krakensdr == 'krakensdr_2':
                data['krakensdr_2']['angles_krakensdr'] = {
                    "max_y": max_y,
                    "x_for_max_y": x_for_max_y_2
                }
                print(f"krakensdr_2: x: {x_for_max_y_2}, y: {max_y}")

            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()

# Function to process JSON data
def process_json_data(json_str, krakensdr):
    try:
        item = json.loads(json_str)
        if item.get('id') == 'mod_n' and 'doa-graph' in item['data']:
            x_values = item['data']['doa-graph']['extendData'][0]['x'][0]
            y_values = item['data']['doa-graph']['extendData'][0]['y'][0]
            update_json(x_values, y_values, krakensdr)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")

# Function to handle WebSocket
async def receive_data(ws_url, krakensdr):
    async with websockets.connect(ws_url) as websocket:
        while True:
            message = await websocket.recv()
            process_json_data(message, krakensdr)

# Function to launch WebSocket for each KrakenSDR
def run_websocket(ws_url, krakensdr):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(receive_data(ws_url, krakensdr))

# Function to launch the Flask web server
def run_flask_app():
    Timer(1, open_browser).start()
    app.run(debug=True, use_reloader=False)

# Open the default browser
def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    # Run Flask and WebSocket for each KrakenSDR in parallel
    flask_thread = Thread(target=run_flask_app)
    websocket_thread_1 = Thread(target=run_websocket, args=(ws_url_1, 'krakensdr_1'))
    websocket_thread_2 = Thread(target=run_websocket, args=(ws_url_2, 'krakensdr_2'))

    flask_thread.start()
    websocket_thread_1.start()
    websocket_thread_2.start()

    flask_thread.join()
    websocket_thread_1.join()
    websocket_thread_2.join()
