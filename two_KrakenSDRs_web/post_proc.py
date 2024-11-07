import json
import os
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
import math
from datetime import datetime
import webbrowser  # Импортируем модуль для открытия страницы в браузере

# Функция для вычисления новых координат на основе расстояния и угла
def calculate_new_point(lat, lon, distance_km, angle_degrees):
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    angle_rad = math.radians(angle_degrees)
    R = 6371.0  # Радиус Земли в километрах
    distance_rad = distance_km / R

    new_lat_rad = math.asin(math.sin(lat_rad) * math.cos(distance_rad) + 
                            math.cos(lat_rad) * math.sin(distance_rad) * math.cos(angle_rad))
    new_lon_rad = lon_rad + math.atan2(math.sin(angle_rad) * math.sin(distance_rad) * math.cos(lat_rad),
                                       math.cos(distance_rad) - math.sin(lat_rad) * math.sin(new_lat_rad))

    new_lat = math.degrees(new_lat_rad)
    new_lon = math.degrees(new_lon_rad)
    return new_lat, new_lon

# Подключение к базе данных и обработка данных
try:
    conn = sqlite3.connect('database/krakensdr_data.db')
    cursor = conn.cursor()

    # Получение данных сессий
    cursor.execute('''
        SELECT session, time,
            CASE 
                WHEN frequency IS NOT NULL THEN frequency
                ELSE (
                    SELECT frequency
                    FROM krakensdr_data AS subquery
                    WHERE subquery.session = krakensdr_data.session
                      AND subquery.frequency IS NOT NULL
                      AND subquery.time > krakensdr_data.time
                    ORDER BY subquery.time
                    LIMIT 1
                )
            END AS frequency
        FROM krakensdr_data
        WHERE time = (
            SELECT MIN(time) 
            FROM krakensdr_data AS subquery
            WHERE subquery.session = krakensdr_data.session
        )
    ''')
    session_data_raw = cursor.fetchall()

    session_data = []
    for session, time_str, frequency in session_data_raw:
        try:
            if 'T' in time_str and '.' in time_str:
                time_obj = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%f')
            elif 'T' in time_str:
                time_obj = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S')
            else:
                time_obj = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')

            formatted_time = time_obj.strftime('%m-%d %H:%M')
            formatted_frequency = 'N/A' if frequency is None else str(frequency)
            session_data.append((session, formatted_time, formatted_frequency))
        except ValueError as e:
            print(f"Error parsing date for session {session}: {e}")


    # Получение данных SDR ID по каждой сессии
    cursor.execute('''
        SELECT session, krakensdr_id, COUNT(*)
        FROM krakensdr_data
        GROUP BY session, krakensdr_id
    ''')
    sdr_id_data = cursor.fetchall()

    # Получение всех данных для вычисления координат и линий
    cursor.execute('SELECT * FROM krakensdr_data')
    rows = cursor.fetchall()

    # Группировка линий по sessionId
    lines_by_session = {}
    coordinates = []

    for row in rows:
        session, time, freq, sdr_id, lat, lon, bearing, direction = row
        if lat is None or lon is None or bearing is None or direction is None:
            continue
        angle = bearing + direction
        new_lat, new_lon = calculate_new_point(lat, lon, 25, angle)
        line = [[lat, lon], [new_lat, new_lon]]
        if session not in lines_by_session:
            lines_by_session[session] = []
        lines_by_session[session].append(line)
        coordinates.append([lat, lon])

finally:
    conn.close()

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path == '/get_coordinates':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    'coordinates': coordinates,
                    'lines_by_session': lines_by_session,
                    'session_data': session_data,
                    'sdr_id_data': sdr_id_data
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                self.path = '/map.html'
                file_path = os.path.join('templates', self.path[1:])
                with open(file_path, 'r') as file:
                    file_to_open = file.read()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(bytes(file_to_open, 'utf-8'))
        except Exception as e:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes(f"Error: {e}", 'utf-8'))

def start_server():
    server_address = 'http://localhost:8000'
    httpd = HTTPServer(('localhost', 8000), RequestHandler)
    print(f"Server started at {server_address}")

    # Открываем страницу в браузере
    webbrowser.open(server_address)

    httpd.serve_forever()

if __name__ == "__main__":
    start_server()
