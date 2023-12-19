import requests, json, pytz
from datetime import datetime
import dateutil
import dateutil.parser
from collections import OrderedDict
from amqp import publish
from apscheduler.schedulers.blocking import BlockingScheduler
from json_schema import JSONSchemaGenerator,schema_validation
from misc.iudx_logging import IudxLogger
import logging
time_formatter = "%Y-%m-%dT%H:%M:%S+05:30"
IST = pytz.timezone("Asia/Kolkata")

exchange_to_publish = "90c70189-e967-4d42-b50d-c2c51d8647e4"
route = "90c70189-e967-4d42-b50d-c2c51d8647e4/.73726452-e3fa-4681-b09c-a19c53d052b7"
ID = "73726452-e3fa-4681-b09c-a19c53d052b7"
schema ={
    "$id": "https://voc.iudx.org.in/TransitManagement",
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "id": {
            "type": "string"
        },
        "stop_id": {
            "anyOf": [{
                "type": "string"
            }, {
                "type": "null"
            }]
        },
        "stop_code": {
            "anyOf": [{
                "type": "string"
            }, {
                "type": "null"
            }]
        },
        "stop_desc": {
            "anyOf": [{
                "type": "string"
            }, {
                "type": "null"
            }]
        },
        "stop_name": {
            "anyOf": [{
                "type": "string"
            }, {
                "type": "null"
            }]
        },
        "location": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string"
                },
                "coordinates": {
                    "type": "array",
                    "items": [{
                            "type": "number"
                        },
                        {
                            "type": "number"
                        }
                    ]
                }
            },
            "required": [
                "type",
                "coordinates"
            ]
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
        "stop_id",
        "stop_code",
        "stop_desc",
        "stop_name",
        "location",
        "observationDateTime"
    ],
    "additionalProperties": False
}

class StopInfo(object):

    def __init__(self,base_url):
        self.base_url = base_url

    def getData(self):
        """
        Extracts route info data.

        Args:

            path(str) : Contains the Url.

        Returns:

            List of Stop info Data.

        """
        try:
            stop_info = (requests.request("GET", self.base_url)).json()
            res=stop_info["data"]            
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
                item["stop_id"] = str(data["stop_id"])
                item["stop_code"] = data["stop_code"]
                item["stop_desc"] = data["stop_type"]
                item["stop_name"] = data["stop_name"]
                item["location"] = {}
                item["location"]["type"] = "Point"
                item["location"]["coordinates"] = [data["stop_lon"],data["stop_lat"]]
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
    url = "https://kdmcportalapi.amnex.com/IDUX/GetStops"
    iudx_logger = IudxLogger(threshold_level=logging.ERROR)
    obj = StopInfo(url)
    obj.getData()
    sched.add_listener(iudx_logger.listener, iudx_logger.EVENT_JOB_MISSED | iudx_logger.EVENT_JOB_MAX_INSTANCES |iudx_logger.EVENT_JOB_ERROR)
    sched.add_job(obj.getData, "interval", days=180)
    sched.start()
