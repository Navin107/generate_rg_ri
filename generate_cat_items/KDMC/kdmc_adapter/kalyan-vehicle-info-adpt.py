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

exchange_to_publish = "90c70189-e967-4d42-b50d-c2c51d8647e4"
route = "90c70189-e967-4d42-b50d-c2c51d8647e4/.fd13f2af-f620-4e59-8418-69d5fd1795b8"
ID = "fd13f2af-f620-4e59-8418-69d5fd1795b8"

schema ={
    "$id": "https://voc.iudx.org.in/TransitManagement",
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "id": {
            "type": "string"
        },
        "license_plate": {
            "anyOf": [{
                "type": "string"
            }, {
                "type": "null"
            }]
        },
        "vehicleType": {
            "anyOf": [{
                "type": "string"               
            }, {
                "type": "null"
            }]
        },
        "acAvailable": {
            "anyOf": [{
                "type": "string"
            }, {
                "type": "null"
            }]
        },
        "vehicleCapacity": {
            "anyOf": [{
                "type": "number"
            }, {
                "type": "null"
            }]
        },
        "deviceID": {
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
        "license_plate",
        "vehicleType",
        "acAvailable",
        "vehicleCapacity",
        "deviceID",
        "observationDateTime"
    ],
    "additionalProperties": False
}
class VehicleInfo(object):

    def __init__(self,base_url):
        self.base_url = base_url

    def getData(self):
        """
        Extracts vehicle info data.

        Args:

            path(str) : Contains the Url.

        Returns:

            List of Vehicle info Data.

        """
        try:
            vehicle_info = (requests.request("GET", self.base_url)).json()
            res=vehicle_info["data"]
            output = self.transformData(res)
            return output
        except IndexError as e:
            print("No data observed for ", e)
        except requests.Timeout as err:
            print("Connection Timeout error.", err)
        except requests.exceptions.ConnectionError:
            print("Connection refused.")

    def transformData(self, res):
        """
        Tranforms the data as per IUDX vocab.

        Args:

            path(list) : List of data.


        """
        publish_packets = []
        try:
            for data in res:
                item = OrderedDict()
                item['id'] = ID
                item["license_plate"] = data["Vehicle_number"]
                item["vehicleType"] = data["Vehicle_type"]
                item["acAvailable"] = data["Service_type"]
                item["vehicleCapacity"] = data["Vehicle_capacity"]
                item["deviceID"] = data["GPS_device_id"]
                item["observationDateTime"] = dateutil.parser.parse(str(datetime.now())).strftime(time_formatter)
                publish_packets.append(item)
            #print(json.dumps(publish_packets, indent=4))             
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
    url = "https://kdmcportalapi.amnex.com/IDUX/GetBusUnitInformation"
    iudx_logger = IudxLogger(threshold_level=logging.ERROR)
    obj = VehicleInfo(url)
    obj.getData()
    sched.add_listener(iudx_logger.listener, iudx_logger.EVENT_JOB_MISSED | iudx_logger.EVENT_JOB_MAX_INSTANCES |iudx_logger.EVENT_JOB_ERROR)
    sched.add_job(obj.getData, "interval", days=180)
    sched.start()
