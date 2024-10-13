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

import requests
import websockets
import asyncio
import json

# Функция для выполнения HTTP-запросов и WebSocket-запросов для заданного IP-адреса и JSON-файла
async def process_freq_request(ip_address, json_file):
    # Открываем страницу /config через HTTP-запрос
    config_url = f"http://{ip_address}:8080/config"
    response = requests.get(config_url)
    print(f"Page /config loaded from {ip_address}, status:", response.status_code)

    # Загружаем данные из JSON-файла
    with open(json_file, 'r') as f:
        message = json.load(f)

    # Отправляем WebSocket-запрос
    ws_url = f"ws://{ip_address}:8080/_push"
    async with websockets.connect(ws_url) as websocket:
        await websocket.send(json.dumps(message))
        response = await websocket.recv()
        print(f"Response from WebSocket on {ip_address}:", response)

    # Открываем страницу /doa через HTTP-запрос
    doa_url = f"http://{ip_address}:8080/doa"
    response = requests.get(doa_url)
    print(f"Page /doa loaded from {ip_address}, status:", response.status_code)

# Запускаем обработку для обоих серверов
async def main():
    await asyncio.gather(
        process_freq_request("10.10.1.93", "freq_rqst_1.json"),
        process_freq_request("10.10.1.93", "freq_rqst_1.json")
    )

# Запускаем основную функцию
if __name__ == "__main__":
    asyncio.run(main())
