from collections import OrderedDict
import requests
import json
import pytz
import time
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import date, timedelta
import dateutil.parser
from amqp import publish
from json_schema import JSONSchemaGenerator, schema_validation
from misc.iudx_logging import IudxLogger
import logging

time_formatter = "%Y-%m-%dT%H:%M:%S+05:30"


exchange_to_publish_old = "skdcl.in/56b48464a1ef630205c17e1a0b538a7664cc103e/kdmc.cop-nec.iudx.org.in/kalyan-dombivli-env-aqm"
route_old = "skdcl.in/56b48464a1ef630205c17e1a0b538a7664cc103e/kdmc.cop-nec.iudx.org.in/kalyan-dombivli-env-aqm/.aqm-info"
ID_old = "skdcl.in/56b48464a1ef630205c17e1a0b538a7664cc103e/kdmc.cop-nec.iudx.org.in/kalyan-dombivli-env-aqm/aqm-info"

exchange_to_publish = "73301321-ce7b-4e46-aa53-1bc30d9b160f"
route = "73301321-ce7b-4e46-aa53-1bc30d9b160f/.b1b02056-5847-42b5-8b9c-12a84a005d5c"
uuid = "b1b02056-5847-42b5-8b9c-12a84a005d5c"

schema_obj = {
	"$id": "https://voc.iudx.org.in/EnvAQM",
	"$schema": "https://json-schema.org/draft/2020-12/schema",
	"type": "object",
	"properties": {
		"id": {
			"type": "string"
		},
		"deviceID": {
			"anyOf": [{
				"type": "string"
			}, {
				"type": "null"
			}]
		},
		"weatherType": {
			"anyOf": [{
				"type": "string"
			}, {
				"type": "null"
			}]
		},
		"precipitation": {
			"anyOf": [{
				"type": "number"
			}, {
				"type": "null"
			}]
		},
		"windSpeed": {
			"anyOf": [{
				"type": "number"
			}, {
				"type": "null"
			}]
		},
		"illuminance": {
			"type": "object",
			"properties": {
				"instValue": {
					"anyOf": [{
						"type": "number"
					}, {
						"type": "null"
					}]
				}
			},
			"required": ["instValue"]
		},
		"so2": {
			"type": "object",
			"properties": {
				"instValue": {
					"anyOf": [{
						"type": "number"
					}, {
						"type": "null"
					}]
				}
			},
			"required": ["instValue"]
		},
		"relativeHumidity": {
			"type": "object",
			"properties": {
				"instValue": {
					"anyOf": [{
						"type": "number"
					}, {
						"type": "null"
					}]
				}
			},
			"required": ["instValue"]
		},
		"pm10": {
			"type": "object",
			"properties": {
				"instValue": {
					"anyOf": [{
						"type": "number"
					}, {
						"type": "null"
					}]
				}
			},
			"required": ["instValue"]
		},
		"pm2p5": {
			"type": "object",
			"properties": {
				"instValue": {
					"anyOf": [{
						"type": "number"
					}, {
						"type": "null"
					}]
				}
			},
			"required": ["instValue"]
		},
		"co": {
			"type": "object",
			"properties": {
				"instValue": {
					"anyOf": [{
						"type": "number"
					}, {
						"type": "null"
					}]
				}
			},
			"required": ["instValue"]
		},
		"no2": {
			"type": "object",
			"properties": {
				"instValue": {
					"anyOf": [{
						"type": "number"
					}, {
						"type": "null"
					}]
				}
			},
			"required": ["instValue"]
		},
		"airTemperature": {
			"type": "object",
			"properties": {
				"instValue": {
					"anyOf": [{
						"type": "number"
					}, {
						"type": "null"
					}]
				}
			},
			"required": ["instValue"]
		},
		"o3": {
			"type": "object",
			"properties": {
				"instValue": {
					"anyOf": [{
						"type": "number"
					}, {
						"type": "null"
					}]
				}
			},
			"required": ["instValue"]
		},
		"co2": {
			"type": "object",
			"properties": {
				"instValue": {
					"anyOf": [{
						"type": "number"
					}, {
						"type": "null"
					}]
				}
			},
			"required": ["instValue"]
		},
		"airQualityIndex": {
			"anyOf": [{
				"type": "number"
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
	"required": ["id", "deviceID", "weatherType", "precipitation", "windSpeed", "illuminance", "so2", "relativeHumidity", "pm10", "pm2p5", "co", "no2", "airTemperature", "o3", "co2", "airQualityIndex", "observationDateTime"],
	"additionalProperties": False
}

ignore_list = [""," ",'NULL',None,"-"," -","-"]

class EnvSensor(object):

    def getData(self):
        """
        :Api is used to get response data .
        :GET method
        :return:
        """
        try:
            url = "http://faridabadwm.ecosmartdc.com/api/Ajeevi/GetEnvDataByRange"

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
            
                if packet:
                    item = OrderedDict()
                    item["id"] = uuid
                    item["deviceID"] = None if packet.get('DeviceId') in ignore_list else  str(packet.get('DeviceId'))
                    item["airQualityIndex"] = None if packet.get('AQI') in ignore_list else  float(packet.get('AQI'))
                    item["weatherType"] = None if packet.get('Alert_Desc') in ignore_list else  str(packet.get('Alert_Desc'))
                    item["observationDateTime"] = dateutil.parser.parse(packet.get('SyncOn')).strftime(time_formatter)
                    item["precipitation"]=  None if packet.get('Rain') in ignore_list else float(packet.get('Rain'))
                    item["windSpeed"] =  None if packet.get('WindSpeed') in ignore_list else float(packet.get('WindSpeed'))
                
                    item["pm2p5"]={}
                    item["pm2p5"]["instValue"] =  None if packet.get('PM2_5') in ignore_list else float(packet.get('PM2_5'))
                
                    item["pm10"]={}
                    item["pm10"]["instValue"] =  None if packet.get('PM10') in ignore_list else float(packet.get('PM10'))
                    
                    item["so2"]={}
                    item["so2"]["instValue"] =  None if packet.get('SO2') in ignore_list else float(packet.get('SO2'))
                
                    item["no2"]={}
                    item["no2"]["instValue"] =  None if packet.get('NO2') in ignore_list else float(packet.get('NO2'))

                    item["co"]={}
                    item["co"]["instValue"] =  None if packet.get('CO') in ignore_list else float(packet.get('CO'))
                
                    item["airTemperature"]={}
                    item["airTemperature"]["instValue"] = None if packet.get('Temperature') in ignore_list else float(packet.get('Temperature'))
                            
                    item["o3"]={}
                    item["o3"]["instValue"] =  None if packet.get('O3') in ignore_list else float(packet.get('O3'))
                    
                    item["co2"]={}
                    item["co2"]["instValue"] =  None if packet.get('CO2') in ignore_list else float(packet.get('CO2'))
                
                    item["relativeHumidity"]={}
                    item["relativeHumidity"]["instValue"] =  None if packet.get('Humidity') in ignore_list else float(packet.get('Humidity'))

                    item["illuminance"]={}
                    item["illuminance"]["instValue"] =  None if packet.get('Light') in ignore_list else float(packet.get('Light'))
                
                    packet_list.append(item)
            
            if packet_list:
                q =schema_validation(packet_list, schema_obj)

            if q.validated_packet:
                #print(json.dumps(packet_list, indent=4))
                publish(exchange=exchange_to_publish, routing_key=route, message=json.dumps(packet_list))
        
        except Exception as e:
                print(e)   

if __name__ == '__main__':
    sched = BlockingScheduler()
    obj = EnvSensor()
    iudx_logger = IudxLogger(threshold_level=logging.ERROR)
    sched.add_job(obj.getData, "cron", hour="01", minute="00")
    sched.add_listener(iudx_logger.listener, iudx_logger.EVENT_JOB_MISSED | iudx_logger.EVENT_JOB_MAX_INSTANCES |
                      iudx_logger.EVENT_JOB_ERROR)
    sched.start()
