import requests
from collections import OrderedDict
import json
import datetime, time
from apscheduler.schedulers.blocking import BlockingScheduler
import pytz
import dateutil.parser
from json_schema import JSONSchemaGenerator, schema_validation
from amqp import publish
from misc.iudx_logging import IudxLogger
import logging

exchange_to_publish = "d16c46dc-adb5-415d-a04b-c5e22e7cf629"
route = "d16c46dc-adb5-415d-a04b-c5e22e7cf629/.d603d1e4-9ffc-42af-837b-4117d37e4d98"
ID = "d603d1e4-9ffc-42af-837b-4117d37e4d98"


schema_obj = {
    "$id": "https://voc.iudx.org.in/IssueReporting",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "id": {
            "type": "string"
        },
        "reportID": {
            "anyOf": [
                {
                    "type": "string"
                },
                {
                    "type": "null"
                }
            ]
        },
        "wardID": {
            "anyOf": [
                {
                    "type": "string"
                },
                {
                    "type": "null"
                }
            ]
        },
        "address": {
            "anyOf": [
                {
                    "type": "string"
                },
                {
                    "type": "null"
                }
            ]
        },
        "resolutionStatus": {
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
        "zoneName": {
            "anyOf": [
                {
                    "type": "string"
                },
                {
                    "type": "null"
                }
            ]
        },
        "comments": {
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
        "department": {
            "anyOf": [
                {
                    "type": "string"
                },
                {
                    "type": "null"
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
        }
    },
    "required": [
        "id",
        "reportID",
        "wardID",
        "address",
        "resolutionStatus",
        "location",
        "zoneName",
        "comments",
        "department",
        "observationDateTime"
    ],
    "additionalProperties": False
}

IST = pytz.timezone("Asia/Kolkata")
cache = {}


ignore_list = [""," ",'NULL',None,"-"," -","-"]
time_formatter = "%Y-%m-%dT%H:%M:%S+05:30"

class CivicIssue():
    
    def getData(self):
        """"API to get data.
        :return: None"""
        try:
            url =  "http://103.41.33.174//MainetService/services/rest/common/citizenDashboardGraph/getDepartmentComplaintsByDaysAndDesc/2"
            api_response = requests.request("GET", url)
            if api_response.status_code != 200:
                time.sleep(300)
                api_response = self.getData()
            
            response_data = api_response.json()
            
            self.publishData(response_data)

        except requests.exceptions.HTTPError as errh:
                print("An Http Error occurred:", errh)

        except requests.exceptions.ConnectionError as errc:
            print("An Error Connecting to the API occurred:", errc)

        except requests.exceptions.Timeout as errt:
            print("A Timeout Error occurred:", errt)

        except requests.exceptions.RequestException as err:
            print("An Unknown Error occurred", err)
        
        

    def publishData(self, data_packets):
        """
            :API is used to transform and publish data accordingly.
            :param data_packets:
            :return: None.
        """
        packet_list = []
        for packet in data_packets:
            item = OrderedDict()
            item["id"] = ID
            item["reportID"] = None if packet.get("complaintNo") in ignore_list else packet.get("complaintNo")
            item["wardID"] = None if packet.get("ward") in ignore_list else packet.get("ward")
            item["zoneName"] = None if packet.get("zone") in ignore_list else packet.get("zone")
            item["address"] = None if packet.get(str("address")) in ignore_list else packet.get(str("address")) 
            item["resolutionStatus"] = None if packet.get(str("status")) in ignore_list else packet.get(str("status"))
            item["comments"] = None if packet.get(str("complaintDesc")) in ignore_list else [packet.get(str("complaintDesc"))]
            item["department"] =  None if packet.get(str("cpdDesc")) in ignore_list else packet.get(str("cpdDesc"))
            item["observationDateTime"] = None if packet.get(str("dateOfRequest")) in ignore_list else dateutil.parser.parse(packet.get(str("dateOfRequest"))).strftime(time_formatter)
            
            item["location"] = OrderedDict()
            cond1 = packet.get('longitude') in ignore_list or packet.get('latitude') in ignore_list
            if cond1:
                item["location"] = None
            else:
                item["location"]["type"] = "Point"
                item["location"]["coordinates"] = [round(float(packet.get('longitude')),6),round(float(packet.get('latitude')),6)]
                
            
            packet_list.append(item)
            
        if packet_list:
           q =schema_validation(packet_list, schema_obj)

        if q.validated_packet:
            #print(json.dumps(packet_list, indent=4))
            publish(exchange=exchange_to_publish, routing_key=route, message=json.dumps(packet_list))

if __name__ == '__main__':
    sched = BlockingScheduler()
    obj = CivicIssue()
    iudx_logger = IudxLogger(threshold_level=logging.ERROR)
    sched.add_job(obj.getData, "cron", hour="23", minute="30")
    sched.add_listener(iudx_logger.listener, iudx_logger.EVENT_JOB_MISSED | iudx_logger.EVENT_JOB_MAX_INSTANCES |
                           iudx_logger.EVENT_JOB_ERROR)
    sched.start()
