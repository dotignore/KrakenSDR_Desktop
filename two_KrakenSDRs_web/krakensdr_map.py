from flask import Flask, render_template, jsonify, request
import json
import math
import webbrowser
from threading import Timer, Thread
import asyncio
import websockets

app = Flask(__name__)

# Global variables for storing x_for_max_y
x_for_max_y_1 = None
x_for_max_y_2 = None

# WebSocket URLs for krakensdr_1 and krakensdr_2
ws_url_1 = "ws://10.10.1.93:8080/_push"
ws_url_2 = "ws://10.10.1.93:8080/_push"

# Function to calculate the endpoint at a certain distance
def calculate_new_point(lat, lon, distance_km, x_for_max_y):
    R = 6371  # Radius of the Earth in kilometers
    bearing = math.radians(x_for_max_y)  # Direction angle in radians, obtained from WebSocket

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
    return render_template('index.html')

# Route to get line data
@app.route('/get_map_data')
def get_map_data():
    global x_for_max_y_1, x_for_max_y_2

    try:
        with open('data.json') as f:
            data = json.load(f)

        # Data for krakensdr_1
        krakensdr_1_data = data.get('krakensdr_1', {})
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
        krakensdr_2_data = data.get('krakensdr_2', {})
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
        return jsonify({'error': 'data.json not found'}), 500

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

    # Update the data.json file with new coordinates
    try:
        with open('data.json', 'r+') as f:
            json_data = json.load(f)
            
            # Update coordinates for the specified KrakenSDR
            json_data[krakensdr]['start_coordinates']['latitude'] = new_lat
            json_data[krakensdr]['start_coordinates']['longitude'] = new_lon
            
            f.seek(0)
            json.dump(json_data, f, indent=4)
            f.truncate()  # Remove the remnants of old data

        return jsonify({'status': 'success'})

    except FileNotFoundError:
        return jsonify({'error': 'data.json not found'}), 500

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

        with open('data.json', 'r+') as f:
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
