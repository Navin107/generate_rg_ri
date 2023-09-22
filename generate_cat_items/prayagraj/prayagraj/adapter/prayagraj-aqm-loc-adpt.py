import json
import requests
import logging
from json_schema import json_schema_generate, schema_validation

from amqp import publish

exchange_to_publish = "9f43cc56-4fa8-489d-af84-11d87e7fe18a"
route = exchange_to_publish + "/.3f8ffa3b-0635-4616-a1e3-701a95daa55c"
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
        device_data = {
            "id": ri_uuid,
            "deviceID": str(aqm_data.get("DeviceID")),
            "name": f"AQM-SENSOR-{aqm_data.get('DeviceID')}",
            "address": None if aqm_data.get("LocationName") is None else str(aqm_data.get("LocationName")),
            "location": {"type": "Point",
                        "coordinates": [None if aqm_data.get('Longitude') is None else float(aqm_data.get('Longitude')),
                                             None if aqm_data.get('Latitude') is None else float(aqm_data.get('Latitude'))]}
        }

        return device_data
    def publish_data(self, list_of_packets):
        """
        publishes data to the message broker.

        :param list_of_packets: list of packets containing aqm data
        :type list_of_packets: List
        """
        q = schema_validation(list_of_packets, schema_obj.json_schema)
        if q.validated_packet:
            #print(route)
            #print(json.dumps(list_of_packets, indent=4))
            publish(exchange=exchange_to_publish, routing_key=route, message=json.dumps(list_of_packets))


if __name__ == "__main__":
    BASE_URL = "http://125.21.250.180:8080"
    device_list = [465, 467, 468, 469, 470, 471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481, 482, 483, 484, 485,
                   486, 487, 488, 489, 490, 491, 492, 493]
    prayagraj_aqm = PrayagrajAqm(BASE_URL)
    schema_obj = json_schema_generate(ri_uuid)

    aqm_cache = {}
    prayagraj_aqm.get_data(device_list)

