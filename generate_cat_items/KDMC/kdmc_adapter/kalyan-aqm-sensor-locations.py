import json
import pandas as pd
from collections import OrderedDict
from json_schema import json_schema_generate, schema_validation
from amqp import publish

exchange_to_publish_old = "skdcl.in/56b48464a1ef630205c17e1a0b538a7664cc103e/kdmc.cop-nec.iudx.org.in/kalyan-dombivli-env-aqm"
route_old = "skdcl.in/56b48464a1ef630205c17e1a0b538a7664cc103e/kdmc.cop-nec.iudx.org.in/kalyan-dombivli-env-aqm/.aqm-sensor-locations"
ID_old = "skdcl.in/56b48464a1ef630205c17e1a0b538a7664cc103e/kdmc.cop-nec.iudx.org.in/kalyan-dombivli-env-aqm/aqm-sensor-locations"

exchange_to_publish = "73301321-ce7b-4e46-aa53-1bc30d9b160f"
route = "73301321-ce7b-4e46-aa53-1bc30d9b160f/.a60e0bd0-7e93-4d9a-b69f-1d52a21fe022"
uuid = "a60e0bd0-7e93-4d9a-b69f-1d52a21fe022"

schema_obj = {
    "$id": "https://voc.iudx.org.in/PointOfInterest",
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
        "name": {
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
        }
    },
    "required": [
        "id",
        "deviceID",
        "name",
        "address",
        "location"
    ],
    "additionalProperties": False
}


def pimpri_chinchwad_poi_transform(path):
     packet_list=[]
     try:
        df = pd.read_csv(path)
     except Exception as e:
        print("Error while accessing the file: ",e)
    
    
     for row in range(0, df.shape[0]):
        dict_packet = {}
        dict_packet["id"] =  uuid
        dict_packet["deviceID"] = str(df.iloc[row,1])
        dict_packet['name'] = "AQM sensor" +" - "+ df.iloc[row,0]
        dict_packet["address"] = df.iloc[row,0]
        dict_packet["location"] = {}
        dict_packet["location"]["type"] = "Point"
        dict_packet["location"]["coordinates"] = [round(float(df.iloc[row,3]),6),round(float(df.iloc[row,2]),6)]  
        packet_list.append(dict_packet)
        
     if packet_list:
         q =schema_validation(packet_list, schema_obj)

     if q.validated_packet:
         #print(json.dumps(packet_list, indent=4))
         publish(exchange=exchange_to_publish, routing_key=route, message=json.dumps(packet_list))


    
if __name__ == "__main__":
    path = "../misc/kalyan-aqm-sensor-locations.csv"
    pimpri_chinchwad_poi_transform(path)
    
