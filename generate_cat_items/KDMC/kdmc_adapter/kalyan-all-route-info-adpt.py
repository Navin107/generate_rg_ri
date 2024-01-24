import requests, json, pytz
from datetime import datetime
import dateutil
import dateutil.parser
from collections import OrderedDict
from amqp import publish
from apscheduler.schedulers.blocking import BlockingScheduler
from json_schema import json_schema_generate, schema_validation
from misc.iudx_logging import IudxLogger
import logging
time_formatter = "%Y-%m-%dT%H:%M:%S+05:30"
IST = pytz.timezone("Asia/Kolkata")

exchange_to_publish_old = "skdcl.in/56b48464a1ef630205c17e1a0b538a7664cc103e/kdmc.cop-nec.iudx.org.in/kalyan-dombivli-itms-info"
route_old = "skdcl.in/56b48464a1ef630205c17e1a0b538a7664cc103e/kdmc.cop-nec.iudx.org.in/kalyan-dombivli-itms-info/.route-info"

exchange_to_publish = "90c70189-e967-4d42-b50d-c2c51d8647e4"
route = "90c70189-e967-4d42-b50d-c2c51d8647e4/.41b63342-9803-4ff9-a09e-c8c2d908d83b"
uuid = "41b63342-9803-4ff9-a09e-c8c2d908d83b"

schema ={
    "$id": "https://voc.iudx.org.in/TransitManagement",
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "id": {
            "type": "string"
        },
        "route_id": {
            "anyOf": [{
                "type": "string"
            }, {
                "type": "null"
            }]
        },
        "route_short_name": {
            "anyOf": [{
                "type": "string"
            }, {
                "type": "null"
            }]
        },
        "route_long_name": {
            "anyOf": [{
                "type": "string"
            }, {
                "type": "null"
            }]
        },
        "route_type": {
            "anyOf": [{
                "type": "number"
            }, {
                "type": "null"
            }]
        },
        "continuous_pickup": {
            "anyOf": [{
                "type": "number"
            }, {
                "type": "null"
            }]
        },
        "continuous_drop_off": {
            "anyOf": [{
                "type": "number"
            }, {
                "type": "null"
            }]
        },
        "travelDistance": {
            "anyOf": [{
                "type": "number"
            }, {
                "type": "null"
            }]
        },
        "travelTime": {
            "anyOf": [{
                "type": "string",
                "format": "time"
            }, {
                "type": "null"
            }]
        },
        "agency_name": {
            "anyOf": [{
                "type": "string"
            }, {
                "type": "null"
            }]
        },
        "agency_url": {
            "anyOf": [{
                "type": "string"
            }, {
                "type": "null"
            }]
        },
        "observationDateTime": {
            "anyOf": [{
                "type": "string",
                "format": "date-time"
            }, {
                "type": "null"
            }]
        }
    },
    "required": [
        "id",
        "route_id",
        "route_short_name",
        "route_long_name",
        "route_type",
        "continuous_pickup",
        "continuous_drop_off",
        "travelDistance",
        "travelTime",
        "agency_name",
        "agency_url",
        "observationDateTime"
    ],
    "additionalProperties": False
}
class RouteInfo(object):


    def __init__(self,base_url):
        self.base_url = base_url

    def getData(self):
        """
        Extracts route info data.

        Args:

            path(str) : Contains the Url.

        Returns:

            List of Route Data.


        """
        try:
            route_info = (requests.request("GET", self.base_url)).json()
            route_info_data=route_info["data"]
            output = self.transformData(route_info_data)
            return output
        except IndexError as e:
            print("No data observed for ", e)
        except requests.Timeout as err:
            print("Connection Timeout error.", err)
        except requests.exceptions.ConnectionError:
            print("Connection refused.")

    def transformData(self, route_info_data):
        """
        Tranforms the data as per IUDX vocab.

        Args:

            path(list) : List of data.


        """

        publish_packets = []
        try:
            for data in route_info_data:
                item = OrderedDict()
                item['id'] = uuid
                item["route_id"] = str(data["route_id"])
                item["route_short_name"] = data["route_short_name"]
                item["route_long_name"] = data["route_long_name"]
                item["route_type"] = data["route_type"]
                item["continuous_pickup"] = data["continuous_pickup"]
                item["continuous_drop_off"] = data["continuous_drop_off"]
                item["travelDistance"] = data["route_km"]
                a = datetime.strptime(data["route_travel_time"], "%H:%M")
                item["travelTime"] = a.strftime("%H:%M:%S")
                item["agency_name"] = "KDMT"
                item["agency_url"] = "https://itskdmc.amnex.com/"
                item["observationDateTime"] = dateutil.parser.parse(str(datetime.now())).strftime(time_formatter)
                publish_packets.append(item)
            if publish_packets:
                q = schema_validation(publish_packets, schema)
                if q.validated_packet:
                    #print(json.dumps(publish_packets, indent=4))
                    publish(exchange=exchange_to_publish, routing_key=route, message=json.dumps(publish_packets))
                else:
                    print("Packets did not adhere to the JSON schema ", publish_packets)

        except Exception as e:
            print(e)
    
if __name__ == "__main__":
    sched = BlockingScheduler()
    BASE_URL = "https://kdmcportalapi.amnex.com/IDUX/GetRoutes"
    iudx_logger = IudxLogger(threshold_level=logging.ERROR)
    obj = RouteInfo(BASE_URL)
    obj.getData()
    sched.add_listener(iudx_logger.listener, iudx_logger.EVENT_JOB_MISSED | iudx_logger.EVENT_JOB_MAX_INSTANCES |iudx_logger.EVENT_JOB_ERROR)
    sched.add_job(obj.getData, "interval", days=180)
    sched.start()
