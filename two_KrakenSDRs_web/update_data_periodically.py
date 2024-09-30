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


import json
import datetime
import asyncio
import websockets
from threading import Thread, Lock

# Global variables for storing x_for_max_y for both WebSocket connections
x_for_max_y_1 = None
x_for_max_y_2 = None

# Lock for thread safety
data_lock = Lock()

ws_url_1 = "ws://10.10.1.93:8080/_push"
ws_url_2 = "ws://10.10.1.93:8080/_push"

# Function to update JSON and get x_for_max_y for ws_url_1
def update_json_1(x_values, y_values):
    global x_for_max_y_1
    if x_values and y_values:
        max_y = max(y_values)
        x_for_max_y_1 = x_values[y_values.index(max_y)]
        output_data_1()

# Function to update JSON and get x_for_max_y for ws_url_2
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
    async with websockets.connect(ws_url_1) as websocket:
        while True:
            message = await websocket.recv()
            process_json_data_1(message)

# Function to handle WebSocket for ws_url_2
async def receive_data_2():
    async with websockets.connect(ws_url_2) as websocket:
        while True:
            message = await websocket.recv()
            process_json_data_2(message)

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
            # Read data from JSON file for KrakenSDR 1
            with open('data_krkn_1.json') as f1:
                data_krakensdr_1 = json.load(f1)
            
            # Get coordinates and directions for KrakenSDR 1
            krakensdr_1_lat = data_krakensdr_1['krakensdr_1']['start_coordinates']['latitude']
            krakensdr_1_lon = data_krakensdr_1['krakensdr_1']['start_coordinates']['longitude']
            krakensdr_1_bearing = data_krakensdr_1['krakensdr_1']['bearing_deg']

            # Get frequency value from JSON
            frequency_value = None
            with open('freq_rqst_1.json') as f:
                freq_data = json.load(f)
                for state in freq_data['data']['state']:
                    if state['id'] == 'daq_center_freq':
                        frequency_value = state['value']
                        break

            # Print the data for KrakenSDR 1
            print_krakensdr_data(1, frequency_value, krakensdr_1_lat, krakensdr_1_lon, krakensdr_1_bearing, x_for_max_y_1)

    except Exception as e:
        print(f"Error outputting data for KrakenSDR 1: {str(e)}")

# Function to output data for KrakenSDR 2
def output_data_2():
    global x_for_max_y_2
    try:
        with data_lock:
            # Read data from JSON file for KrakenSDR 2
            with open('data_krkn_2.json') as f2:
                data_krakensdr_2 = json.load(f2)
            
            # Get coordinates and directions for KrakenSDR 2
            krakensdr_2_lat = data_krakensdr_2['krakensdr_2']['start_coordinates']['latitude']
            krakensdr_2_lon = data_krakensdr_2['krakensdr_2']['start_coordinates']['longitude']
            krakensdr_2_bearing = data_krakensdr_2['krakensdr_2']['bearing_deg']

            # Get frequency value from JSON
            frequency_value = None
            with open('freq_rqst_1.json') as f:
                freq_data = json.load(f)
                for state in freq_data['data']['state']:
                    if state['id'] == 'daq_center_freq':
                        frequency_value = state['value']
                        break

            # Print the data for KrakenSDR 2
            print_krakensdr_data(2, frequency_value, krakensdr_2_lat, krakensdr_2_lon, krakensdr_2_bearing, x_for_max_y_2)

    except Exception as e:
        print(f"Error outputting data for KrakenSDR 2: {str(e)}")

# Function to print KrakenSDR data
def print_krakensdr_data(sdr_id, frequency_value, latitude, longitude, bearing, direction):
    current_time = datetime.datetime.now().isoformat()
    print(f"Time: {current_time}, Freq: {frequency_value} MHz, KrakenSDR {sdr_id}: N={latitude}, E={longitude}, B={bearing}°, D={direction}°")

if __name__ == '__main__':
    # Run WebSocket 1 in a separate thread
    websocket_thread_1 = Thread(target=run_websocket_1)
    websocket_thread_1.start()

    # Run WebSocket 2 in a separate thread
    websocket_thread_2 = Thread(target=run_websocket_2)
    websocket_thread_2.start()

    # Ensure that the WebSocket threads join back
    websocket_thread_1.join()
    websocket_thread_2.join()
