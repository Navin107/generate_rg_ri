import time
import json
import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from amqp import publish
from collections import OrderedDict
import dateutil.parser
from datetime import date, timedelta
import pytz
from json_schema import json_schema_generate, schema_validation
from misc.iudx_logging import IudxLogger
import logging

IST = pytz.timezone("Asia/Kolkata")
time_formatter = "%Y-%m-%dT%H:%M:%S+05:30"

exchange_to_publish_old = "skdcl.in/56b48464a1ef630205c17e1a0b538a7664cc103e/kdmc.cop-nec.iudx.org.in/kalyan-dombivli-flood"
route_old = "skdcl.in/56b48464a1ef630205c17e1a0b538a7664cc103e/kdmc.cop-nec.iudx.org.in/kalyan-dombivli-flood/.water-level-info"
ID_old = "skdcl.in/56b48464a1ef630205c17e1a0b538a7664cc103e/kdmc.cop-nec.iudx.org.in/kalyan-dombivli-flood/water-level-info"

exchange_to_publish = "800c242d-0fea-409c-903c-a4fb22c7d27e"
route = "800c242d-0fea-409c-903c-a4fb22c7d27e/.015deffe-ffcd-4566-b6a9-0333d768bfdf"
uuid = "015deffe-ffcd-4566-b6a9-0333d768bfdf"


schema_obj = {
    "$id": "https://voc.iudx.org.in/WaterDistributionNetwork",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "id": {
            "type": "string"
        },
        "deviceID": {
            "anyOf": [
                {
                    "type": "string"
                },
                {
                    "type": "null"
                }
            ]
        },
        "currentLevel": {
            "anyOf": [
                {
                    "type": "number"
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
        "deviceID",
        "currentLevel",
        "observationDateTime"
    ],
    "additionalProperties": False
}

ignore_list = [""," ",'NULL',None,"-"," -","-"]

class kalyan_flood(object):
    
    def getData(self):
        try:
            url = "http://faridabadwm.ecosmartdc.com/api/Iothub/GetFloodDataByRange"

            prev_day = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
            payload = json.dumps({
            "FromDate": prev_day,
            "ToDate": prev_day
            })
            headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ZW52OmVudiMyMDIw'
            }

            api_response = requests.request("POST", url, headers=headers, data=payload)

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
            
            packet_list = []
            try:
                for packet in data_packets:
                    item = OrderedDict()
                    item['id'] = uuid
                    item["deviceID"] = None if packet.get('DeviceId') in ignore_list else  str(packet.get('DeviceId'))
                    item["currentLevel"] = None if packet.get('Lvl') in ignore_list else  float(packet.get('Lvl'))
                    item["observationDateTime"] = dateutil.parser.parse(packet.get('SyncOn')).strftime(time_formatter)
                    packet_list.append(item)
                    
                if packet_list:
                    q =schema_validation(packet_list, schema_obj)

                if q.validated_packet:
                    #print(json.dumps(packet_list, indent=4))
                    publish(exchange=exchange_to_publish, routing_key=route, message=json.dumps(packet_list))
            
            except AttributeError as e:
                print("AttributeError :", e)
            
if __name__ == '__main__':
    sched = BlockingScheduler()
    obj = kalyan_flood()
    iudx_logger = IudxLogger(threshold_level=logging.ERROR)
    sched.add_job(obj.getData, "cron", hour="01", minute="00")
    sched.add_listener(iudx_logger.listener, iudx_logger.EVENT_JOB_MISSED | iudx_logger.EVENT_JOB_MAX_INSTANCES |
                      iudx_logger.EVENT_JOB_ERROR)
    sched.start()

