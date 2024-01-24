import requests
import json
import datetime
import dateutil
import dateutil.parser
import pytz
from apscheduler.schedulers.blocking import BlockingScheduler
from json_schema import json_schema_generate, schema_validation
from misc.iudx_logging import IudxLogger
import logging
from amqp import publish

exchange_to_publish = "skdcl.in/56b48464a1ef630205c17e1a0b538a7664cc103e/kdmc.cop-nec.iudx.org.in/kalyan-dombivli-itms-info"
route = "skdcl.in/56b48464a1ef630205c17e1a0b538a7664cc103e/kdmc.cop-nec.iudx.org.in/kalyan-dombivli-itms-info/.kalyan-itms-info"
IST = pytz.timezone("Asia/Kolkata")

exchange_to_publish = "90c70189-e967-4d42-b50d-c2c51d8647e4"
route = "90c70189-e967-4d42-b50d-c2c51d8647e4/.58e3d173-c0b5-4e65-991b-5e47ffccc9cf"
ID = "58e3d173-c0b5-4e65-991b-5e47ffccc9cf"

time_formatter = "%Y-%m-%dT%H:%M:%S+05:30"


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
        "location": {
      "type": "object",
      "properties": {
        "type": {
          "type": "string"
        },
        "coordinates": {
          "type": "array",
          "items": [
            {
              "type": "array",
              "items": [
                {
                  "type": "number"
                },
                {
                  "type": "number"
                }
              ]
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "number"
                },
                {
                  "type": "number"
                }
              ]
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "number"
                },
                {
                  "type": "number"
                }
              ]
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "number"
                },
                {
                  "type": "number"
                }
              ]
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "number"
                },
                {
                  "type": "number"
                }
              ]
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "number"
                },
                {
                  "type": "number"
                }
              ]
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "number"
                },
                {
                  "type": "number"
                }
              ]
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "number"
                },
                {
                  "type": "number"
                }
              ]
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "number"
                },
                {
                  "type": "number"
                }
              ]
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "number"
                },
                {
                  "type": "number"
                }
              ]
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "number"
                },
                {
                  "type": "number"
                }
              ]
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "number"
                },
                {
                  "type": "number"
                }
              ]
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "number"
                },
                {
                  "type": "number"
                }
              ]
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "number"
                },
                {
                  "type": "number"
                }
              ]
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "number"
                },
                {
                  "type": "number"
                }
              ]
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "number"
                },
                {
                  "type": "number"
                }
              ]
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "number"
                },
                {
                  "type": "number"
                }
              ]
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "number"
                },
                {
                  "type": "number"
                }
              ]
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "number"
                },
                {
                  "type": "number"
                }
              ]
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "number"
                },
                {
                  "type": "number"
                }
              ]
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "number"
                },
                {
                  "type": "number"
                }
              ]
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "number"
                },
                {
                  "type": "number"
                }
              ]
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "number"
                },
                {
                  "type": "number"
                }
              ]
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "number"
                },
                {
                  "type": "number"
                }
              ]
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "number"
                },
                {
                  "type": "number"
                }
              ]
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "number"
                },
                {
                  "type": "number"
                }
              ]
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "number"
                },
                {
                  "type": "number"
                }
              ]
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "number"
                },
                {
                  "type": "number"
                }
              ]
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "number"
                },
                {
                  "type": "number"
                }
              ]
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
        "location",
        "observationDateTime"
    ],
    "additionalProperties": False
}


class RouteShapes(object):

    def __init__(self, base_url):
        self.base_url = base_url

    def getData(self):
        """
        Extracts route shape info data.

        Args:

            path(str) : Contains the Url.

        Returns:

            List of Route Data.


        """
        result = {}
        shape_points={}
        try:
            response = (requests.request("GET", self.base_url)).json()
            res = response["data"]
            for packet in res:
                if packet["shape_id"] not in result:
                    result[packet["shape_id"]] = [packet["shape_pt_sequence"]]
                else:
                    result[packet["shape_id"]].append(packet["shape_pt_sequence"])
                    result[packet["shape_id"]].sort()
            for data in res:
                shape_points[data["shape_pt_sequence"]] = [round(float(data["shape_pt_lon"]),6), round(float(data['shape_pt_lat']),6)]
            self.transformData(result,shape_points)
        except IndexError as e:
            print("No data observed for ", e)
        except requests.Timeout as err:
            print("Connection Timeout error.", err)
        except Exception as e:
            print("error while querying the API", e)


    def transformData(self,result,shape_points):
        """
        Tranforms the data as per IUDX vocab.

        Args:

            path(list) : List of data.


        """

        transform_output = []
        for key in result.keys():
            route_with_stop_coordinates = {
                'id': ID,
                'route_id': str(key),
                'location': {
                    'type': 'LineString',
                    'coordinates': [],
                },
                "observationDateTime":dateutil.parser.parse(str(datetime.datetime.now())).strftime(time_formatter)
            }
            for point in result[key]:
                route_with_stop_coordinates['location']['coordinates'].append(shape_points.get(point, [None, None]))
            transform_output.append(route_with_stop_coordinates)
        if transform_output:
            q = schema_validation(transform_output, schema)
            if q.validated_packet:
                #print(json.dumps(transform_output, indent=4))
                publish(exchange=exchange_to_publish, routing_key=route, message=json.dumps(transform_output))
            else:
                print("Packets did not adhere to the JSON schema ", transform_output)


if __name__ == "__main__":
  sched = BlockingScheduler()
  BASE_URL = "https://kdmcportalapi.amnex.com/IDUX/getshape"
  iudx_logger = IudxLogger(threshold_level=logging.ERROR)
  obj = RouteShapes(BASE_URL)
  obj.getData()
  sched.add_job(obj.getData, "interval", days=180)
  sched.add_listener(iudx_logger.listener, iudx_logger.EVENT_JOB_MISSED | iudx_logger.EVENT_JOB_MAX_INSTANCES |iudx_logger.EVENT_JOB_ERROR)
  sched.start()
