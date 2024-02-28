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



        with open("D:/iudx/generate_rg_ri/generate_cat_items/generated_data/generate-resource-item-data-arrival-interval-latest.jsonld", 'r+', encoding='utf-8') as fp:
            json_str = fp.read()
            json_array = json.loads(json_str)


        # list_uuid = []

        # json_array_ids = [i["id"] for i in json_array]
        # new_json_array_ids = [i["id"] for i in new_json_array]

        # for i in new_json_array_ids:
        #     if i not in json_array_ids:
        #         list_uuid.append(i)

        # print(len(list_uuid))

        # print(list_uuid)


        # for iii in list_uuid:

        #     requests.get(f"https://cos.iudx.org.in/iudx/cat/v1/item?id=058eacc1-477d-4971-9fc7-4df4193cc90a")

        # requests.get()




        # json_changed_dict = []
        # ids = [self.df.iloc[row,6] for row in range(0, self.df.shape[0])]
        json_new = []
        
        for json_data in json_array:
            json_data = OrderedDict(json_data)

     
         
            # if json_data["id"] in ids:
            #     self.iloc_function(json_data["id"], json_data)

            # else:
            #     if json_data.get("iudxResourceAPIs", None):
            #         if "TEMPORAL" in json_data["iudxResourceAPIs"]:
            #             json_data["dataArrivalInterval"] = "temporal"
            #         elif "TEMPORAL" not in json_data["iudxResourceAPIs"] and "ATTR" in json_data["iudxResourceAPIs"]:
            #             json_data["dataArrivalInterval"] = "nonTemporal"


            if not json_data.get("instance", None):
                ff = json_data["resourceGroup"]
                json_data["instance"] = requests.get(f"https://cos.iudx.org.in/iudx/cat/v1/item?id={ff}").json()["results"][0]["instance"]





            # elif json_data.get("iudxResourceAPIs", None):
            #     if "TEMPORAL" in json_data["iudxResourceAPIs"]:
            #     json_data["dataArrivalInterval"] = "temporal"


            # # elif json_data["type"][1]== "iudx:Camera" and "TEMPORAL" in json_data["iudxResourceAPIs"]:
            # #     json_data["dataArrivalInterval"] = "temporal"  

            # # elif json_data["type"][1]== "iudx:GISData":
            # #     json_data["dataArrivalInterval"] = "nonTemporal"  
            
            # else:
                
            #     if json_data.get("dataSample", None):
                
            #         if json_data["dataSample"].get("observationDateTime", None):
            #             json_data["dataArrivalInterval"] = "TBC"      
                
            #         else:
            #             json_data["dataArrivalInterval"] = "nonTemporal"
                
            #     else:
            #         json_data["dataArrivalInterval"] = "TBC"      


            desired_keys = [
                "@context", "id", "type",  "name", "label", "description", "tags", "accessPolicy", "apdURL",
                "provider", "resourceServer", "resourceGroup", "resourceType", "iudxResourceAPIs",
                "dataArrivalInterval", "dataDescriptor", "dataSample", "dataSampleFile", "location",
                "itemStatus", "instance", "ownerUserId", "cos", "itemCreatedAt"
            ]

            json_new.append(self.extract_desired_keys(desired_keys, json_data))
        
        return json_new


data_processor = IUDXDataProcessor()
uuid_data = data_processor.generate()

with open("../generated_data/generate-resource-item-data-arrival-interval-new-updated.jsonld", "w") as f:
    json.dump(uuid_data,f,indent=5)

print("done")


