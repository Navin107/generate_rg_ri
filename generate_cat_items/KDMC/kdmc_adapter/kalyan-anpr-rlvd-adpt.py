import pandas as pd
import json
from json_schema import json_schema_generate, schema_validation
from collections import OrderedDict
from amqp import publish

exchange_to_publish_old = "skdcl.in/56b48464a1ef630205c17e1a0b538a7664cc103e/kdmc.cop-nec.iudx.org.in/kalyan-dombivli-point-of-interests"
route_old = "skdcl.in/56b48464a1ef630205c17e1a0b538a7664cc103e/kdmc.cop-nec.iudx.org.in/kalyan-dombivli-point-of-interests/.traffic-camera-locations"

exchange_to_publish = "ec49c89e-35c7-4554-a695-4bc8ea7bf298"
route = "ec49c89e-35c7-4554-a695-4bc8ea7bf298/.f7253922-6d59-4054-968c-eb10b56c7843"
uuid = "f7253922-6d59-4054-968c-eb10b56c7843"

schema ={
    "$id": "https://voc.iudx.org.in/PointOfInterest",
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "id": {
            "type": "string"
        },
        "name": {
            "anyOf": [{
                "type": "string"
            }, {
                "type": "null"
            }]
        },
        "deviceCount": {
            "anyOf": [{
                "type": "number"
            }, {
                "type": "null"
            }]
        },
        "address": {
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
    }
  },
    "required": [
        "id",
        "name",
        "address",
        "location"
    ],
    "additionalProperties": False
}

def kalyan_poi_transform(path):
    """
        Extracts traffic camera locations and tranforms the data as per IUDX vocab.

        Args:

            path(str) : Contains the path of the source file.


    """    
    try:
        df = pd.read_csv(path)  	
        
    except Exception as e:
        print("Error while accessing the file")
        print(e)
    
    id = route.split("point-of-interests/.")[1]
    final_packet = []
    for row in range(0, df.shape[0]):    
        item = {}
        item["id"] =   exchange_to_publish +"/"+ id 
        item['name'] = "ANPR and RLVD Camera" +" - "+ df.iloc[row,0]
        item["address"] = df.iloc[row,0] 
        item["deviceCount"] = int(df.iloc[row,3]) 
        item["location"] = {}
        item["location"]["type"] = "Point"
        item["location"]["coordinates"] = [round(df.iloc[row,2],6),round(df.iloc[row,1],6)]  
        final_packet.append(item)
    #print(json.dumps(final_packet, indent=4))
    if final_packet:     
        q = schema_validation(final_packet, schema)
        if q.validated_packet:
            #print(json.dumps(final_packet, indent=4))
            publish(exchange=exchange_to_publish, routing_key=route, message=json.dumps(final_packet))
        else:
            print("Packets did not adhere to the JSON schema ", final_packet)

    return None

if __name__ == "__main__":    
    path = "../misc/kalyan_anpr_rlvd_locations.csv"
    kalyan_poi_transform(path)
    
