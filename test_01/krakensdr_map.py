# python3.12 -m venv venv
# source venv/bin/activate
# pip3 install flask
# pip3 install websockets
# pip3 install requests

from flask import Flask, render_template, jsonify, request
import json
import math
import webbrowser
from threading import Timer, Thread
import asyncio
import websockets
import requests


app = Flask(__name__)


config_url = "http://10.10.1.93:8080/config"
doa_url = "http://10.10.1.93:8080/doa"
ws_url = "ws://10.10.1.93:8080/_push"
json_file_path = 'freq_rqst_1.json'  # Укажи правильный путь к файлу


# Global variables for storing x_for_max_y
x_for_max_y_1 = None
x_for_max_y_2 = None

# Function to calculate the endpoint at a certain distance and bearing
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

# Function to load WebSocket URLs from JSON files
def load_ws_urls():
    try:
        with open('data_krkn_1.json') as f1, open('data_krkn_2.json') as f2:
            data_krakensdr_1 = json.load(f1)
            data_krakensdr_2 = json.load(f2)

        ws_url_1 = data_krakensdr_1['krakensdr_1'].get('ws_url', None)
        ws_url_2 = data_krakensdr_2['krakensdr_2'].get('ws_url', None)

        return ws_url_1, ws_url_2

    except FileNotFoundError:
        print("One or both data files not found.")
        return None, None

def get_frequency_from_json():
    try:
        with open(json_file_path, 'r') as f:
            freq_data = json.load(f)
            frequency_value = freq_data['data']['state'][0]['value']
            print(f"Loaded frequency: {frequency_value}")  # Debug print
            return frequency_value
    except FileNotFoundError:
        print("JSON file not found, using default frequency 103.0")  # Debug print
        return 103.0  # значение по умолчанию, если файл не найден
    except KeyError:
        print("Key not found in JSON, using default frequency 103.0")  # Debug print
        return 103.0  # значение по умолчанию, если ключ не найден



# Обработка загрузки страницы /config
@app.route('/load_config', methods=['GET'])
def load_config():
    response = requests.get(config_url)
    return f"Config page loaded, status: {response.status_code}"

# Обработка загрузки страницы /doa
@app.route('/load_doa', methods=['GET'])
def load_doa():
    response = requests.get(doa_url)
    return f"DOA page loaded, status: {response.status_code}"

def send_websocket_request_in_thread(message):
    asyncio.run(send_websocket_request(message))

async def send_websocket_request(message):
    async with websockets.connect(ws_url) as websocket:
        await websocket.send(json.dumps(message))
        response = await websocket.recv()
        print("Response from WebSocket:", response)

# Обновление частоты в freq_rqst_1.json
@app.route('/update_frequency', methods=['POST'])
def update_frequency():
    data = request.get_json()
    frequency_value = data.get('value')

    # Преобразуем значение в число, если оно передано как строка
    try:
        frequency_value = float(frequency_value)
    except ValueError:
        return jsonify({"error": "Invalid frequency value"}), 400

    # Обновление JSON файла
    with open(json_file_path, 'r') as f:
        freq_data = json.load(f)

    # Обновляем частоту как число, а не строку
    freq_data['data']['state'][0]['value'] = frequency_value

    with open(json_file_path, 'w') as f:
        json.dump(freq_data, f, indent=4)

    # Запуск WebSocket запроса в отдельном потоке
    Thread(target=send_websocket_request_in_thread, args=(freq_data,)).start()

    # Выполнение HTTP-запроса к /doa после отправки WebSocket
    doa_response = requests.get(doa_url)
    print(f"Page /doa loaded, status: {doa_response.status_code}")

    return jsonify({"status": "success", "message": f"Frequency updated to {frequency_value}", "doa_status": doa_response.status_code})




# Route for the main page
@app.route('/')
def index():
    frequency_value = get_frequency_from_json()
    return render_template('index.html', frequency_value=frequency_value)


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

# Route to update bearing value
@app.route('/update_bearing/<krakensdr_id>', methods=['POST'])
def update_bearing(krakensdr_id):
    file_name = 'data_krkn_1.json' if krakensdr_id == '1' else 'data_krkn_2.json'
    try:
        data = request.json
        new_bearing = data.get('bearing_deg')

        if new_bearing is None:
            return jsonify({'error': 'No bearing value provided'}), 400

        # Update the bearing_deg in the correct file
        with open(file_name, 'r+') as f:
            json_data = json.load(f)
            json_data[f'krakensdr_{krakensdr_id}']['bearing_deg'] = float(new_bearing)
            f.seek(0)
            json.dump(json_data, f, indent=4)
            f.truncate()

        return jsonify({'status': 'success'})

    except FileNotFoundError:
        return jsonify({'error': 'Data file not found'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to get bearing value
@app.route('/get_bearing_value/<krakensdr_id>')
def get_bearing_value(krakensdr_id):
    file_name = 'data_krkn_1.json' if krakensdr_id == '1' else 'data_krkn_2.json'
    try:
        with open(file_name) as f:
            data = json.load(f)
            bearing_deg = data[f'krakensdr_{krakensdr_id}'].get('bearing_deg', 0)
        return jsonify({'bearing_deg': bearing_deg})
    except FileNotFoundError:
        return jsonify({'error': 'Data file not found'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
    # Load WebSocket URLs
    ws_url_1, ws_url_2 = load_ws_urls()

    if ws_url_1 is None or ws_url_2 is None:
        print("Failed to load WebSocket URLs")
        exit(1)

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
