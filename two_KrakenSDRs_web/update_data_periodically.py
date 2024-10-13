# GNU GENERAL PUBLIC LICENSE
# Version 3, 29 June 2007
#
# Copyright (C) 2024 Tarasenko Volodymyr hc158b@gmail.com https://github.com/dotignore/KrakenSDR_Desktop/
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

import sqlite3
import json
import datetime
import asyncio
import websockets
from flask import Flask, request, jsonify
from threading import Thread, Lock
import os

# Create Flask app instance
app = Flask(__name__)

# Global variables for storing x_for_max_y for both WebSocket connections
x_for_max_y_1 = None
x_for_max_y_2 = None

# Lock to ensure thread safety
data_lock = Lock()

# WebSocket URLs
ws_url_1 = "ws://10.10.1.93:8080/_push"
ws_url_2 = "ws://10.10.1.93:8080/_push"

# Function to get the latest session value from the database
def get_latest_session():
    conn = sqlite3.connect('database/krakensdr_data.db')  # Path to your database
    cursor = conn.cursor()
    cursor.execute('SELECT MAX(session) FROM krakensdr_data')
    latest_session = cursor.fetchone()[0]
    conn.close()
    return latest_session if latest_session is not None else 0

# Function to update JSON and retrieve x_for_max_y for ws_url_1
def update_json_1(x_values, y_values):
    global x_for_max_y_1
    if x_values and y_values:
        max_y = max(y_values)
        x_for_max_y_1 = x_values[y_values.index(max_y)]
        output_data_1()

# Function to update JSON and retrieve x_for_max_y for ws_url_2
def update_json_2(x_values, y_values):
    global x_for_max_y_2
    if x_values and y_values:
        max_y = max(y_values)
        x_for_max_y_2 = x_values[y_values.index(max_y)]
        output_data_2()

# Function to process JSON data for ws_url_1
def process_json_data_1(json_str):
    try:
        item = json.loads(json_str)
        if item.get('id') == 'mod_n' and 'doa-graph' in item['data']:
            x_values = item['data']['doa-graph']['extendData'][0]['x'][0]
            y_values = item['data']['doa-graph']['extendData'][0]['y'][0]
            update_json_1(x_values, y_values)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON (ws_url_1): {e}")

# Function to process JSON data for ws_url_2
def process_json_data_2(json_str):
    try:
        item = json.loads(json_str)
        if item.get('id') == 'mod_n' and 'doa-graph' in item['data']:
            x_values = item['data']['doa-graph']['extendData'][0]['x'][0]
            y_values = item['data']['doa-graph']['extendData'][0]['y'][0]
            update_json_2(x_values, y_values)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON (ws_url_2): {e}")

# Function to handle WebSocket for ws_url_1
async def receive_data_1():
    try:
        async with websockets.connect(ws_url_1) as websocket:
            while True:
                message = await websocket.recv()
                process_json_data_1(message)
    except Exception as e:
        print(f"Error connecting to WebSocket 1: {e}")

# Function to handle WebSocket for ws_url_2
async def receive_data_2():
    try:
        async with websockets.connect(ws_url_2) as websocket:
            while True:
                message = await websocket.recv()
                process_json_data_2(message)
    except Exception as e:
        print(f"Error connecting to WebSocket 2: {e}")

# Function to run WebSocket 1 in a separate thread
def run_websocket_1():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(receive_data_1())

# Function to run WebSocket 2 in a separate thread
def run_websocket_2():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(receive_data_2())

# Function to output data for KrakenSDR 1
def output_data_1():
    global x_for_max_y_1
    try:
        with data_lock:
            if os.path.exists('data_krkn_1.json'):
                with open('data_krkn_1.json') as f1:
                    data_krakensdr_1 = json.load(f1)
                
                krakensdr_1_lat = data_krakensdr_1['krakensdr_1']['start_coordinates']['latitude']
                krakensdr_1_lon = data_krakensdr_1['krakensdr_1']['start_coordinates']['longitude']
                krakensdr_1_bearing = data_krakensdr_1['krakensdr_1']['bearing_deg']

                # Retrieve frequency value from JSON
                frequency_value = None
                if os.path.exists('freq_rqst_1.json'):
                    with open('freq_rqst_1.json') as f:
                        freq_data = json.load(f)
                        for state in freq_data['data']['state']:
                            if state['id'] == 'daq_center_freq':
                                frequency_value = state['value']
                                break

                print_krakensdr_data(1, frequency_value, krakensdr_1_lat, krakensdr_1_lon, krakensdr_1_bearing, x_for_max_y_1)
            else:
                print("Data file for KrakenSDR 1 not found")
    except Exception as e:
        print(f"Error outputting data for KrakenSDR 1: {str(e)}")

# Function to output data for KrakenSDR 2
def output_data_2():
    global x_for_max_y_2
    try:
        with data_lock:
            if os.path.exists('data_krkn_2.json'):
                with open('data_krkn_2.json') as f2:
                    data_krakensdr_2 = json.load(f2)
                
                krakensdr_2_lat = data_krakensdr_2['krakensdr_2']['start_coordinates']['latitude']
                krakensdr_2_lon = data_krakensdr_2['krakensdr_2']['start_coordinates']['longitude']
                krakensdr_2_bearing = data_krakensdr_2['krakensdr_2']['bearing_deg']

                # Retrieve frequency value from JSON
                frequency_value = None
                if os.path.exists('freq_rqst_1.json'):
                    with open('freq_rqst_1.json') as f:
                        freq_data = json.load(f)
                        for state in freq_data['data']['state']:
                            if state['id'] == 'daq_center_freq':
                                frequency_value = state['value']
                                break

                print_krakensdr_data(2, frequency_value, krakensdr_2_lat, krakensdr_2_lon, krakensdr_2_bearing, x_for_max_y_2)
            else:
                print("Data file for KrakenSDR 2 not found")
    except Exception as e:
        print(f"Error outputting data for KrakenSDR 2: {str(e)}")

# Function to insert data into the database
def insert_data(time, frequency, krakensdr_id, latitude, longitude, bearing, direction, session_id):
    print(f"Inserting data into DB: Time={time}, Freq={frequency}, ID={krakensdr_id}, Lat={latitude}, Lon={longitude}, Bearing={bearing}, Dir={direction}, Session={session_id}")
    
    conn = sqlite3.connect('database/krakensdr_data.db')
    cursor = conn.cursor()

    # Измените 'timestamp' на 'time', как в структуре таблицы
    cursor.execute('''
        INSERT INTO krakensdr_data (time, frequency, krakensdr_id, latitude, longitude, bearing, direction, session)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (time, frequency, krakensdr_id, latitude, longitude, bearing, direction, session_id))
    
    conn.commit()
    conn.close()


# Function to print KrakenSDR data and insert into SQLite database
def print_krakensdr_data(sdr_id, frequency_value, latitude, longitude, bearing, direction):
    current_time = datetime.datetime.now().isoformat()  # Текущее время будет храниться в 'time'
    session_id = get_latest_session()  # Получаем актуальный session
    
    # Debugging output to verify the extracted data
    #print(f"Time: {current_time}, Freq: {frequency_value} MHz, KrakenSDR: {sdr_id}, Lat: {latitude}, Lon: {longitude}, Bearing: {bearing}, Direction: {direction}, Session: {session_id}")
    
    # Передаем 'current_time' вместо 'timestamp'
    insert_data(current_time, frequency_value, sdr_id, latitude, longitude, bearing, direction, session_id)



# Function to update frequency and increment session
@app.route('/update_frequency_and_session', methods=['POST'])
def update_frequency_and_session():
    data = request.get_json()
    frequency = data.get('frequency')

    if frequency is None:
        return jsonify({"status": "error", "message": "Frequency is required"}), 400
    
    # Increment session
    latest_session = get_latest_session()
    new_session = latest_session + 1

    # Open SQLite connection
    conn = sqlite3.connect('database/krakensdr_data.db')
    cursor = conn.cursor()

    # Insert new session and frequency
    cursor.execute('INSERT INTO krakensdr_data (session, frequency) VALUES (?, ?)', (new_session, frequency))
    
    conn.commit()
    conn.close()

    return jsonify({"status": "success", "session": new_session, "frequency": frequency})

if __name__ == '__main__':
    # Run WebSocket in separate threads
    websocket_thread_1 = Thread(target=run_websocket_1)
    websocket_thread_1.start()

    websocket_thread_2 = Thread(target=run_websocket_2)
    websocket_thread_2.start()

    # Run Flask app
    app.run(debug=True)

    # Wait for threads to complete
    websocket_thread_1.join()
    websocket_thread_2.join()
