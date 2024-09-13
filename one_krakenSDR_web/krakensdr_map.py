# source venv/bin/activate

from flask import Flask, render_template, jsonify, request
import json
import math
import webbrowser
from threading import Timer, Thread
import asyncio
import websockets

app = Flask(__name__)

# Global variable for storing x_for_max_y
x_for_max_y = None

# Function to calculate the endpoint at a certain distance
def calculate_new_point(lat, lon, distance_km, x_for_max_y):
    R = 6371  # Earth's radius in kilometers
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
    global x_for_max_y  # Using the global variable x_for_max_y

    with open('data.json') as f:
        data = json.load(f)

    start_lat = data['start_coordinates']['latitude']
    start_lon = data['start_coordinates']['longitude']
    distance_km = data['distance_km']
    bearing_deg = data['bearing_deg']
    bearing_deg

    # If x_for_max_y exists, add 50 degrees
    if x_for_max_y is not None:
        x_for_max_y_modified = (x_for_max_y + bearing_deg) % 360  # Add 50 degrees and take modulo 360
        end_lat, end_lon = calculate_new_point(start_lat, start_lon, distance_km, x_for_max_y_modified)
    else:
        # If x_for_max_y has not been received yet, return the initial coordinates
        end_lat, end_lon = start_lat, start_lon

    return jsonify({
        'start_lat': start_lat,
        'start_lon': start_lon,
        'end_lat': end_lat,
        'end_lon': end_lon
    })

# Route for updating marker coordinates
@app.route('/update_coordinates', methods=['POST'])
def update_coordinates():
    data = request.json  # Get data from the request
    new_lat = data.get('latitude')
    new_lon = data.get('longitude')

    # Update the data.json file with new coordinates
    with open('data.json', 'r+') as f:
        json_data = json.load(f)
        json_data['start_coordinates']['latitude'] = new_lat
        json_data['start_coordinates']['longitude'] = new_lon
        f.seek(0)
        json.dump(json_data, f, indent=4)
        f.truncate()  # Remove remnants of old data

    return jsonify({'status': 'success'})

@app.route('/update_bearing', methods=['POST'])
def update_bearing():
    new_bearing = request.json.get('bearing_deg')
    
    # Load data from data.json
    with open('data.json', 'r') as f:
        data = json.load(f)
    
    # Update the bearing_deg value
    data['bearing_deg'] = float(new_bearing)
    
    # Save the updated data back to data.json
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)
    
    return jsonify({"status": "success"}), 200

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

# Function to run the Flask web server
def run_flask_app():
    Timer(1, open_browser).start()
    app.run(debug=True, use_reloader=False)

# websocket_code.py (embedded in this script for convenience)
ws_url = "ws://10.10.1.93:8080/_push"

# Function to update JSON and get x_for_max_y
def update_json(x_values, y_values):
    global x_for_max_y  # Declare global variable for use
    if x_values and y_values:
        max_y = max(y_values)
        x_for_max_y = x_values[y_values.index(max_y)]  # Update the global variable value
        
        with open('data.json', 'r+') as f:
            data = json.load(f)
            data['angles_krakensdr'] = {
                "max_y": max_y,
                "x_for_max_y": x_for_max_y
            }
            
            print(f"x: {x_for_max_y}, y: {max_y}")
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()

# Function to process JSON data
def process_json_data(json_str):
    global x_values, y_values
    try:
        item = json.loads(json_str)
        if item.get('id') == 'mod_n' and 'doa-graph' in item['data']:
            x_values = item['data']['doa-graph']['extendData'][0]['x'][0]
            y_values = item['data']['doa-graph']['extendData'][0]['y'][0]
            update_json(x_values, y_values)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")

# Function to handle WebSocket
async def receive_data():
    async with websockets.connect(ws_url) as websocket:
        while True:
            message = await websocket.recv()
            process_json_data(message)

# Function to run WebSocket in a separate thread
def run_websocket():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(receive_data())

if __name__ == '__main__':
    # Run Flask and WebSocket in parallel
    flask_thread = Thread(target=run_flask_app)
    websocket_thread = Thread(target=run_websocket)

    flask_thread.start()
    websocket_thread.start()

    flask_thread.join()
    websocket_thread.join()
