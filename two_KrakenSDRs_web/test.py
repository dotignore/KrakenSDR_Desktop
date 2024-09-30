import json
import time
import datetime

# Функция для обновления данных каждые 1000 миллисекунд
def update_data_periodically():
    while True:
        try:
            # Чтение данных из файлов JSON
            with open('data_krkn_1.json') as f1:
                data_krakensdr_1 = json.load(f1)
            
            # Получение координат и направлений для обеих систем KrakenSDR
            krakensdr_1_lat = data_krakensdr_1['krakensdr_1']['start_coordinates']['latitude']
            krakensdr_1_lon = data_krakensdr_1['krakensdr_1']['start_coordinates']['longitude']
            krakensdr_1_bearing = data_krakensdr_1['krakensdr_1']['bearing_deg']

            # Выводим текущую частоту (допустим, частота берется из первого JSON файла)
            frequency_value = None
            with open('freq_rqst_1.json') as f:
                freq_data = json.load(f)
                for state in freq_data['data']['state']:
                    if state['id'] == 'daq_center_freq':
                        frequency_value = state['value']
                        break

            # Вывод данных в консоль
            current_time = datetime.datetime.now().isoformat()
            print(f"Time: {current_time}")
            print(f"Frequency: {frequency_value} MHz")
            print(f"KrakenSDR 1: Latitude={krakensdr_1_lat}, Longitude={krakensdr_1_lon}, Bearing={krakensdr_1_bearing}°")
            print("---------------------------------------------------")

        except Exception as e:
            print(f"Error updating data: {str(e)}")

        # Задержка на 1000 миллисекунд (1 секунда)
        time.sleep(1)

if __name__ == '__main__':
    update_data_periodically()
