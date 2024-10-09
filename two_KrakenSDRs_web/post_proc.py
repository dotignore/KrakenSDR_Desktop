import webbrowser
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import math
import sqlite3

# Function to calculate new coordinates based on distance and angle
def calculate_new_point(lat, lon, distance_km, angle_degrees):
    # Convert latitude, longitude, and angle to radians
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    angle_rad = math.radians(angle_degrees)

    # Distance to radians (distance / Earth's radius)
    R = 6371.0  # Radius of the Earth in kilometers
    distance_rad = distance_km / R

    # Calculate new latitude and longitude using spherical trigonometry
    new_lat_rad = math.asin(math.sin(lat_rad) * math.cos(distance_rad) + 
                            math.cos(lat_rad) * math.sin(distance_rad) * math.cos(angle_rad))

    new_lon_rad = lon_rad + math.atan2(math.sin(angle_rad) * math.sin(distance_rad) * math.cos(lat_rad),
                                       math.cos(distance_rad) - math.sin(lat_rad) * math.sin(new_lat_rad))

    # Convert new coordinates from radians back to degrees
    new_lat = math.degrees(new_lat_rad)
    new_lon = math.degrees(new_lon_rad)

    return new_lat, new_lon

# Connect to the database
conn = sqlite3.connect('database/krakensdr_data.db')
cursor = conn.cursor()

# Execute SQL query to select all data from the krakensdr_data table
cursor.execute('SELECT * FROM krakensdr_data')
rows = cursor.fetchall()

# Prepare data for map (coordinates and lines)
lines = []
coordinates = []

if rows:
    for row in rows:
        time, freq, sdr_id, lat, lon, bearing, direction = row
        angle = bearing + direction  # Calculate the total angle
        new_lat, new_lon = calculate_new_point(lat, lon, 25, angle)  # 25 km line length
        lines.append([[lat, lon], [new_lat, new_lon]])
        coordinates.append([lat, lon])
else:
    print("No data found in the database.")

# Close the connection to the database
conn.close()

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/get_coordinates':
            # Return data in JSON format (initial coordinates and lines)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'coordinates': coordinates,
                'lines': lines
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            # Return HTML file
            if self.path == '/' or self.path == '/map.html':
                self.path = '/map.html'
            try:
                file_path = os.path.join('templates', self.path[1:])
                with open(file_path, 'r') as file:
                    file_to_open = file.read()
                self.send_response(200)
            except Exception as e:
                self.send_response(404)
                file_to_open = "File not found. Error: " + str(e)
            self.end_headers()
            self.wfile.write(bytes(file_to_open, 'utf-8'))

def start_server():
    httpd = HTTPServer(('localhost', 8000), RequestHandler)
    print("Server started at http://localhost:8000")
    webbrowser.open('http://localhost:8000')
    httpd.serve_forever()

if __name__ == "__main__":
    start_server()
