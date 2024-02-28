import json
import requests
from collections import OrderedDict
import uuid
import pandas as pd

class IUDXDataProcessor:
    
    def __init__(self):
        
        file_path = 'D:/iudx/generate_rg_ri/generate_cat_items/raw/adapter_freq.xlsx'
        self.df = pd.read_excel(file_path, sheet_name='Dynamic')
    
    def fetch_url_data(self, url):

        response = requests.get(url)
        dict_data = response.json()
        json_array = dict_data.get("results", [])
        return json_array

    def extract_desired_keys(self, desired_keys, json_data):
        
        return {key: json_data[key] for key in desired_keys if json_data.get(key)}
    
    def iloc_function(self, id_val, json_data):

        for row in range(0, self.df.shape[0]): 
            if self.df.iloc[row, 6]==id_val:
                json_data["dataArrivalInterval"] = self.df.iloc[row, 3]
           
    def generate(self):

        url = "https://cos.iudx.org.in/iudx/cat/v1/search?property=[type]&value=[[iudx:ResourceGroup]]"
        json_array = self.fetch_url_data(url)

        # json_changed_dict = []
        # ids = [self.df.iloc[row,6] for row in range(0, self.df.shape[0])]
        # json_new = []
        
        for json_data in json_array:
            json_data = OrderedDict(json_data)

     
         
        #     if json_data["id"] in ids:
        #         self.iloc_function(json_data["id"], json_data)

        #     else:
        #         if json_data.get("iudxResourceAPIs", None):
        #             if "TEMPORAL" in json_data["iudxResourceAPIs"]:
        #                 json_data["dataArrivalInterval"] = "temporal"
        #             elif "TEMPORAL" not in json_data["iudxResourceAPIs"] and "ATTR" in json_data["iudxResourceAPIs"]:
        #                 json_data["dataArrivalInterval"] = "nonTemporal"




        #     # elif json_data.get("iudxResourceAPIs", None):
        #     #     if "TEMPORAL" in json_data["iudxResourceAPIs"]:
        #     #     json_data["dataArrivalInterval"] = "temporal"


        #     # # elif json_data["type"][1]== "iudx:Camera" and "TEMPORAL" in json_data["iudxResourceAPIs"]:
        #     # #     json_data["dataArrivalInterval"] = "temporal"  

        #     # # elif json_data["type"][1]== "iudx:GISData":
        #     # #     json_data["dataArrivalInterval"] = "nonTemporal"  
            
        #     # else:
                
        #     #     if json_data.get("dataSample", None):
                
        #     #         if json_data["dataSample"].get("observationDateTime", None):
        #     #             json_data["dataArrivalInterval"] = "TBC"      
                
        #     #         else:
        #     #             json_data["dataArrivalInterval"] = "nonTemporal"
                
        #     #     else:
        #     #         json_data["dataArrivalInterval"] = "TBC"      


            desired_keys = [
                    "@context", "id", "id_bck", "type",  "name", "label", "description", "tags", "accessPolicy", "apdURL",
                    "provider", "provider_bck", "resourceServer", "resourceServer_bck",
                    "resourceGroup", "resourceGroup_bck" ,  "resourceType",  "iudxResourceAPIs",
                    "dataDescriptor", "dataSample", "dataSampleFile",
                    "itemStatus", "instance", "ownerUserId", "itemCreatedAt"
                ]

            json_new.append(self.extract_desired_keys(desired_keys, json_data))
        
        return json_new


data_processor = IUDXDataProcessor()
uuid_data = data_processor.generate()

with open("../generated_data/generate-resource-group-arrival-interval.jsonld", "w") as f:
    json.dump(uuid_data,f,indent=5)

print("done")


