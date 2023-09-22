import json
import requests
import dateutil.parser as dp
from datetime import datetime
import pytz
from apscheduler.schedulers.blocking import BlockingScheduler
from iudx_logging import IudxLogger
from json_schema import json_schema_generate, schema_validation
import logging

from amqp import publish

tz = pytz.timezone('asia/kolkata')
exchange_to_publish = "9f43cc56-4fa8-489d-af84-11d87e7fe18a"
route = exchange_to_publish + "/.9014d2ad-f612-4d2c-9eff-fdc75938ef3c"
ri_uuid=route.split('/.')[1]

class PrayagrajAqm:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_data(self, device_list):
        """
        Extracts aqm properties from the source api
        :param device_list:list of device id's
        :type device_list:list
        """
        url = self.base_url + "/cities/prayagraj/data/devices/batch"
        headers = {
            'Auth-Token': 'yMhFBYUiPGqj9WV0T8uXWlfEJDUrIrI65IphSRetaCGCaMkuDIAvOOxLfwUsNpsr',
            'Content-Type': 'application/json'
        }
        payload = json.dumps({
            "devices": device_list
        })

        aqm_list = []
        device_status_list = []
        try:
            aqm_response = requests.get(url, headers=headers, data=payload)
            aqm_list = aqm_response.json().get('data')

        except requests.exceptions.HTTPError as errh:
            print("An Http Error occurred:", errh)

        except requests.exceptions.ConnectionError as errc:
            print("An Error Connecting to the API occurred:")

        except requests.exceptions.Timeout as errt:
            print("A Timeout Error occurred:", errt)

        except requests.exceptions.RequestException as err:
            print("An Unknown Error occurred", err)

        except Exception as oe:
            print('other errors:', oe)

        if aqm_list:
            # print(aqm_list)
            # print(len(aqm_list))
            list_of_packets = list(map(self.transform_data, aqm_list))
            self.publish_data(list_of_packets)
        else:
            error_msg = 'data not available due to the above errors'
            print(error_msg)

    def transform_data(self, aqm_data):
        """
        Transforms the list of packets as per IUDX vocab
        :param aqm_list:List of packets containing aqm properties
        :type aqm_list:list
        """
        if aqm_data.get("Timestamp") is not None:
            dt = datetime.strptime(aqm_data.get("Timestamp"), '%d-%m-%Y %H:%M:%S')
            timestamp=datetime.strftime(dt, '%Y-%m-%dT%H:%M:%S+05:30')
        device_data = {
            "id":ri_uuid ,
            "deviceID": str(aqm_data.get("DeviceID")),
            "deviceStatus": aqm_data.get("ConnectionStatus"),
            "observationDateTime": timestamp,
            "airQualityIndex": None if aqm_data.get('AQI') is None else int(aqm_data.get('AQI')),
            "airQualityLevel": None if aqm_data.get('LocationStatus') is None else str(aqm_data.get('LocationStatus')),
            "aqiMajorPollutant": None if aqm_data.get('MajorPollutant') is None else str(aqm_data.get('MajorPollutant'))
        }

        parameter_values = {}

        for param in aqm_data['ParameterValues']:
            if param.get("Name") == 'SO2':
                parameter_values["so2"] = {}
                parameter_values["so2"]["avgOverTime"] = float(param['Value'].split()[0])
            elif param.get("Name") == 'Temperature':
                parameter_values["airTemperature"] = {}
                parameter_values["airTemperature"]["avgOverTime"] = float(param['Value'].split()[0])
            elif param.get("Name") == 'PM10':
                parameter_values["pm10"] = {}
                parameter_values["pm10"]["avgOverTime"] = float(param['Value'].split()[0])
            elif param.get("Name") == 'CO2':
                parameter_values["co2"] = {}
                parameter_values["co2"]["avgOverTime"] = float(param['Value'].split()[0])
            elif param.get("Name") == 'Noise':
                parameter_values["ambientNoise"] = {}
                parameter_values["ambientNoise"]["avgOverTime"] = float(param['Value'].split()[0])
            elif param.get("Name") == 'Humidity':
                parameter_values["relativeHumidity"] = {}
                parameter_values["relativeHumidity"]["avgOverTime"] = float(param['Value'].split()[0])
            elif param.get("Name") == 'Pressure':
                parameter_values["atmosphericPressure"] = {}
                parameter_values["atmosphericPressure"]["avgOverTime"] = float(param['Value'].split()[0])
            elif param.get("Name") == 'NO2':
                parameter_values["no2"] = {}
                parameter_values["no2"]["avgOverTime"] = float(param['Value'].split()[0])
            elif param.get("Name") == 'PM2.5':
                parameter_values["pm2p5"] = {}
                parameter_values["pm2p5"]["avgOverTime"] = float(param['Value'].split()[0])
            elif param.get("Name") == 'CO':
                parameter_values["co"] = {}
                parameter_values["co"]["avgOverTime"] = float(param['Value'].split()[0])

        device_data.update(parameter_values)
        return device_data

    def deduplication(self, current_sensor):
        """
        Removes duplicates from current_list of packets for each cycle &
        Stores list of packets seen in each cycle as json dump.

        :param aqm_dict: Packet obtained at each cycle
        :type aqm_dict: dict
        """
        if current_sensor["deviceID"] in aqm_cache.keys():
            # existing sensors check observationDateTime
            if dp.parse(current_sensor["observationDateTime"]) > dp.parse(
                    aqm_cache[current_sensor["deviceID"]]["observationDateTime"]):
                aqm_cache[current_sensor["deviceID"]]["observationDateTime"] = current_sensor["observationDateTime"]
                return current_sensor
        else:
            # new sensors
            aqm_cache[current_sensor["deviceID"]] = current_sensor
            return current_sensor

    def publish_data(self, list_of_packets):
        """
        publishes data to the message broker.

        :param list_of_packets: list of packets containing aqm data
        :type list_of_packets: List
        """
        aqm_data = [packet for packet in list(map(self.deduplication, list_of_packets)) if packet is not None]
        q = schema_validation(aqm_data, schema_obj.json_schema)
        if q.validated_packet:
            #print(route)
            #print(json.dumps(aqm_data, indent=4))
            publish(exchange=exchange_to_publish, routing_key=route, message=json.dumps(aqm_data))


if __name__ == "__main__":
    BASE_URL = "http://125.21.250.180:8080"
    device_list = [465, 467, 468, 469, 470, 471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481, 482, 483, 484, 485,
                   486, 487, 488, 489, 490, 491, 492, 493]
    prayagraj_aqm = PrayagrajAqm(BASE_URL)
    aqm_cache = {}
    prayagraj_aqm.get_data(device_list)
    scheduler = BlockingScheduler()
    # subsequent publish
    scheduler.add_job(prayagraj_aqm.get_data, 'interval', hours=1, args=[device_list])
    iudx_logger = IudxLogger(threshold_level=logging.ERROR)
    schema_obj = json_schema_generate(ri_uuid)
    scheduler.add_listener(iudx_logger.listener,
                       iudx_logger.EVENT_JOB_MISSED | iudx_logger.EVENT_JOB_MAX_INSTANCES |
                       iudx_logger.EVENT_JOB_ERROR)

    scheduler.start()
