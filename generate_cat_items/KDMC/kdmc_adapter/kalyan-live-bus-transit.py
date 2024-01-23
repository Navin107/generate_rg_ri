import json
import logging
import requests
import dateutil.parser as dp
import datetime as dtime
import pytz
from apscheduler.schedulers.blocking import BlockingScheduler
from amqp import publish
from json_schema import schema_validation
from misc.iudx_logging import IudxLogger
from json_schema import json_schema_generate, schema_validation


tz = pytz.timezone('GMT')
exchange_to_publish = "90c70189-e967-4d42-b50d-c2c51d8647e4"
route = "90c70189-e967-4d42-b50d-c2c51d8647e4/.18d724d1-6736-41b4-8e65-0592b87bf670"
ID= "18d724d1-6736-41b4-8e65-0592b87bf670"



schema_obj = {
    "$id": "https://voc.iudx.org.in/TransitManagement",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "id": {
            "type": "string"
        },
        "route_id": {
            "anyOf": [
                {
                    "type": "string"
                },
                {
                    "type": "null"
                }
            ]
        },
        "license_plate": {
            "anyOf": [
                {
                    "type": "string"
                },
                {
                    "type": "null"
                }
            ]
        },
        "actual_trip_start_time": {
            "anyOf": [
                {
                    "type": "string",
                    "format": "date-time"
                },
                {
                    "type": "null"
                }
            ]
        },
        "last_stop_arrival_time": {
            "anyOf": [
                {
                    "type": "string",
                    "format": "time"
                },
                {
                    "type": "null"
                }
            ]
        },
        "speed": {
            "anyOf": [
                {
                    "type": "number"
                },
                {
                    "type": "null"
                }
            ]
        },
        "stopScheduleRelationship": {
            "anyOf": [
                {
                    "type": "string"
                },
                {
                    "type": "null"
                }
            ]
        },
        "start_date": {
            "anyOf": [
                {
                    "type": "string",
                    "format": "date"
                },
                {
                    "type": "null"
                }
            ]
        },
        "start_time": {
            "anyOf": [
                {
                    "type": "string",
                    "format": "time"
                },
                {
                    "type": "null"
                }
            ]
        },
        "trip_id": {
            "anyOf": [
                {
                    "type": "string"
                },
                {
                    "type": "null"
                }
            ]
        },
        "last_stop_id": {
            "anyOf": [
                {
                    "type": "string"
                },
                {
                    "type": "null"
                }
            ]
        },
        "location": {
            "anyOf": [
                {
                    "type": "null"
                },
                {
                    "type": "object",
                    "properties": {
                        "coordinates": {
                            "type": "array",
                            "items": {
                                "type": "number"
                            }
                        }
                    }
                }
            ]
        },
        "observationDateTime": {
            "anyOf": [
                {
                    "type": "string",
                    "format": "date-time"
                },
                {
                    "type": "null"
                }
            ]
        },
        "bearing": {
            "anyOf": [
                {
                    "type": "number"
                },
                {
                    "type": "null"
                }
            ]
        },
        "vehicleID": {
            "anyOf": [
                {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                {
                    "type": "string"
                },
                {
                    "type": "null"
                }
            ]
        },
        "direction_id": {
            "anyOf": [
                {
                    "type": "number"
                },
                {
                    "type": "null"
                }
            ]
        },
        "schedule_relationship": {
            "anyOf": [
                {
                    "type": "string"
                },
                {
                    "type": "null"
                }
            ]
        }
    },
    "required": [
        "id",
        "route_id",
        "license_plate",
        "actual_trip_start_time",
        "last_stop_arrival_time",
        "speed",
        "stopScheduleRelationship",
        "start_date",
        "start_time",
        "trip_id",
        "last_stop_id",
        "location",
        "observationDateTime",
        "bearing",
        "vehicleID",
        "direction_id",
        "schedule_relationship"
    ],
    "additionalProperties": False
}


class KalyanDombivil:
    """
    A class for live bus tracking
    """

    def __init__(self, base_url):
        self.base_url = base_url

    def get_data(self):
        """
        Extracts live bus tracking info from the source api
        """
        url = BASE_URL + "IDUX/GetBusliveLocation"

        list_of_packets = []
        eta_response = ""
        try:
            eta_response = requests.get(url)
            list_of_packets = eta_response.json()['data']

        except requests.exceptions.HTTPError:
            print("An Http Error occurred:")

        except requests.exceptions.ConnectionError:
            print("An Error Connecting to the API occurred:")

        except requests.exceptions.Timeout:
            print("A Timeout Error occurred:")

        except requests.exceptions.RequestException as err:
            print("An Unknown Error occurred")

        except Exception as e:
            print('other errors:', e)

        if eta_response.status_code == 400:
            self.get_data()

        if list_of_packets:
            # print(list_of_packets[0])
            self.transform_data(list_of_packets)

        else:
            error_msg = 'data not available due to the above errors'
            print(error_msg)

    def transform_data(self, list_of_packets):
        """
        Transforms the json properties from the source API as per IUDX vocab

        Args:
            list_of_packets(List):list of json packets containing live bus data
        """
        bus_list = []
        res_id = ID

        for packet in list_of_packets:
            dt = None if packet.get('timestamp') is None else str(
                dtime.datetime.fromtimestamp(int(packet.get('timestamp')), tz))
            dt = dt.split('+')[0] + "+05:30"
            st_day = None if packet.get('start_date') is None else packet.get('start_date').split()[0][0:2]
            st_month = None if packet.get('start_date') is None else packet.get('start_date').split()[0][2:4]
            st_year = None if packet.get('start_date') is None else packet.get('start_date').split()[0][4:]
            bus_dict = {
                "id": res_id,
                "trip_id": None if packet.get('trip_id') is None or len(str(packet.get('trip_id'))) == 0 else str(
                    packet.get('trip_id')),
                "bearing": None if packet.get('heading') is None else float(packet.get('heading')),
                "actual_trip_start_time": None if packet.get('actual_tripstarttime') is None or len(
                    packet.get('actual_tripstarttime')) == 0 else str(f"{st_year}-{st_month}-{st_day}") + "T" + str(
                    packet.get('actual_tripstarttime')) + "+05:30",
                "stopScheduleRelationship": None if packet.get('stop_schedule_relationship') is None or len(
                    packet.get('stop_schedule_relationship')) == 0 else str(packet.get('stop_schedule_relationship')),
                "route_id": None if packet.get('routeid') is None or len(str(packet.get('routeid'))) == 0 else str(
                    packet.get('routeid')),
                "location": {'type': 'Point',
                             'coordinates': [
                                 float(packet.get('longitude')) if float(packet.get('longitude')) is not None else None,
                                 float(packet.get('lattitude')) if float(packet.get('lattitude')) is not None else None]
                             },
                "vehicleID": None if packet.get('vehicleid') is None or len(str(packet.get('vehicleid'))) == 0 else str(
                    packet.get('vehicleid')),
                "license_plate": None if packet.get('vehicle_label') is None or len(
                    packet.get('vehicle_label')) == 0 else str(packet.get('vehicle_label')),
                "last_stop_id": None if packet.get('stop_id') is None or len(packet.get('stop_id')) == 0 else str(
                    packet.get('stop_id')),
                "observationDateTime": dt.replace(' ', 'T'),
                "start_date": str(f"{st_year}-{st_month}-{st_day}"),
                "start_time": None if packet.get('start_time') is None or len(packet.get('start_time')) == 0 else str(
                    packet.get('start_time')),
                "last_stop_arrival_time": None if packet.get('arrival_time') is None or len(
                    packet.get('arrival_time')) == 0 else str(packet.get('arrival_time')),
                "speed": None if packet.get('speed') is None else float(
                    packet.get('speed')),
                "direction_id": None if packet.get('direction_id') is None else int(
                    packet.get('direction_id')),
                "schedule_relationship": None if packet.get('trip_schedule_relationship') is None or len(
                    packet.get('trip_schedule_relationship')) == 0 else str(packet.get('trip_schedule_relationship')),

            }
            bus_list.append(bus_dict)
        self.publish_data(bus_list)

    def deduplication(self, current_vehicle):
        """
        Removes duplicates from current_list of packets for each cycle &
        stores list of packets seen in each cycle as json dump.

        Args:
            current_vehicle(Dictionary):Packet obtained at each cycle
        """
        if current_vehicle["license_plate"] in bus_cache.keys():
            # existing sensors check observationDateTime
            if dp.parse(current_vehicle["observationDateTime"]) > dp.parse(
                    bus_cache[current_vehicle["license_plate"]]["observationDateTime"]):
                bus_cache[current_vehicle["license_plate"]]["observationDateTime"] = current_vehicle[
                    "observationDateTime"]
                return current_vehicle
        else:
            # new sensors
            bus_cache[current_vehicle["license_plate"]] = current_vehicle
            return current_vehicle

    def publish_data(self, list_of_packets):
        """
        Publishes data to the message broker.

        Args:
            list_of_packets(List): list of packets containing live bus data
        """
        bus_eta_list = [packet for packet in list(map(self.deduplication, list_of_packets)) if packet is not None]
        q = schema_validation(bus_eta_list,schema_obj)
        if q.validated_packet:
            #print(json.dumps(q.validated_packet, indent=4))
            publish(exchange=exchange_to_publish, routing_key=route, message=json.dumps(q.validated_packet))


if __name__ == "__main__":
    BASE_URL = "https://kdmcportalapi.amnex.com/"
    live_bus = KalyanDombivil(BASE_URL)
    bus_cache = {}
    iudx_logger = IudxLogger(threshold_level=logging.ERROR)
    scheduler = BlockingScheduler()
    # first publish
    live_bus.get_data()
    # subsequent publish
    scheduler.add_job(live_bus.get_data, 'interval', seconds=10,max_instances=3)
    scheduler.add_listener(iudx_logger.listener,
                           iudx_logger.EVENT_JOB_MISSED | iudx_logger.EVENT_JOB_MAX_INSTANCES |
                           iudx_logger.EVENT_JOB_ERROR)
    scheduler.start()