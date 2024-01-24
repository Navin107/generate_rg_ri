import json
import pandas as pd
from collections import OrderedDict
from json_schema import json_schema_generate, schema_validation
from amqp import publish

exchange_to_publish = "800c242d-0fea-409c-903c-a4fb22c7d27e"
route = "800c242d-0fea-409c-903c-a4fb22c7d27e/.9413508c-24da-418e-aaa1-9b721d2d4fe7"
ID = "9413508c-24da-418e-aaa1-9b721d2d4fe7"

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

def sensorLocations(path):
     packet_list=[]
     try:
        df = pd.read_csv(path)
     except Exception as e:
        print("Error while accessing the file: ",e) 
    
    
     for row in range(0, df.shape[0]):
        print(df.iloc[row])
        dict_packet = {}
        dict_packet["id"] =   ID
        dict_packet["deviceID"] = str(df.iloc[row,1])
        dict_packet['name'] = "Flood sensor" +" - "+ df.iloc[row,0]
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
    path = "../misc/kalyan-flood-sensor-locations.csv"
    sensorLocations(path)
    
