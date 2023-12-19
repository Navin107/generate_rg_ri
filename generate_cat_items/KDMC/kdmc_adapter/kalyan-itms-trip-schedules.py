from datetime import date
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import requests
import json
import pytz
from amqp import publish
from json_schema import JSONSchemaGenerator, schema_validation
from misc.iudx_logging import IudxLogger
import logging

exchange_to_publish = "90c70189-e967-4d42-b50d-c2c51d8647e4"
route = "90c70189-e967-4d42-b50d-c2c51d8647e4/.18d724d1-6736-41b4-8e65-0592b87bf670"
IST = pytz.timezone("Asia/Kolkata")
ID = "18d724d1-6736-41b4-8e65-0592b87bf670"

schema = {
	"$id": "https://voc.iudx.org.in/TransitManagement",
	"$schema": "http://json-schema.org/draft-04/schema#",
	"type": "object",
	"properties": {
		"id": {
			"type": "string"
		},
		"trip_id": {
			"anyOf": [{
				"type": "string"
			}, {
				"type": "null"
			}]
		},
		"stop_id": {
			"anyOf": [{
				"type": "string"
			}, {
				"type": "null"
			}]
		},
		"arrival_time": {
			"anyOf": [{
				"type": "string",
				"format": "time"
			}, {
				"type": "null"
			}]
		},
		"departure_time": {
			"anyOf": [{
				"type": "string",
				"format": "time"
			}, {
				"type": "null"
			}]
		},
		"stop_sequence": {
			"anyOf": [{
				"type": "number"
			}, {
				"type": "null"
			}]
		},
		"direction_id": {
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
	"required": [
		"id",
		"trip_id",
		"stop_id",
		"arrival_time",
		"departure_time",
		"stop_sequence",
		"direction_id",
		"observationDateTime"
	],
	"additionalProperties": False
}

class KalyanTransit():

    def getSchedules(self):
        """
          :Method to fetch all the bus arrival schedules of all stops along all trips of the current day
        """
        try:
            url = "https://kdmcportalapi.amnex.com/IDUX/GetStopTime"
            payload = {}
            headers = {}

            res = requests.request("GET", url, headers=headers, data=payload)
            self.transformData(res.json()["data"])

        except Exception as e:
            print("Exception Occurred in stop schedules API", e)

    def transformData(self, response):
        """
        :Method is used to transform data according to our data model.
        :param response: List of packets from the southbound API response
        """
        transformedOutput = []
        for packet in response:
            final_data = dict()
            final_data["id"] = ID
            final_data["trip_id"] = str(packet["tripid"])
            final_data["stop_id"] = str(packet["stop_id"])
            final_data["arrival_time"] = packet["Stop_arrival_time"]
            final_data["departure_time"] = packet["Stop_departure_time"]
            final_data["stop_sequence"] = packet["Stop_seq"]
            final_data["direction_id"] = packet["direction_id"]
            datetime_obj = datetime.strptime(str(datetime.now().replace(microsecond=0)), "%Y-%m-%d %H:%M:%S")
            iudx_date_format = datetime_obj.astimezone(IST).isoformat()
            final_data["observationDateTime"] = iudx_date_format

            transformedOutput.append(final_data)
        q = schema_validation(transformedOutput, schema)
        if q.validated_packet:
            #print(json.dumps(transformedOutput, indent=4))
            publish(exchange=exchange_to_publish, routing_key=route, message=json.dumps(transformedOutput))
        else:
            print("Packets did not adhere to the JSON schema ", transformedOutput)

if __name__ == "__main__":
    sched = BlockingScheduler()
    obj = KalyanTransit()
    obj.getSchedules()
    iudx_logger = IudxLogger(threshold_level=logging.ERROR)
    sched.add_job(obj.getSchedules, "cron", day="1", hour="1")
    sched.add_listener(iudx_logger.listener, iudx_logger.EVENT_JOB_MISSED | iudx_logger.EVENT_JOB_MAX_INSTANCES |
                           iudx_logger.EVENT_JOB_ERROR)
    sched.start()