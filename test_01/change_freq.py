import requests
import websockets
import asyncio
import json

# Open the page through an HTTP request (headless)
config_url = "http://10.10.1.93:8080/config"
response = requests.get(config_url)
print("Page /config loaded, status:", response.status_code)

# Load data from freq_rqst_1.json
with open('freq_rqst_1.json', 'r') as f:
    message = json.load(f)

# Send WebSocket request
async def send_websocket_request():
    ws_url = "ws://10.10.1.93:8080/_push"
    
    async with websockets.connect(ws_url) as websocket:
        await websocket.send(json.dumps(message))
        response = await websocket.recv()
        print("Response from WebSocket:", response)

# Launch WebSocket client
asyncio.run(send_websocket_request())

# Open the page /doa through an HTTP request (headless)
doa_url = "http://10.10.1.93:8080/doa"
response = requests.get(doa_url)
print("Page /doa loaded, status:", response.status_code)
