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



        with open("D:/iudx/generate_rg_ri/generate_cat_items/generated_data/extra_data.jsonld", 'r+', encoding='utf-8') as fp:
            json_str = fp.read()
            json_array = json.loads(json_str)
        json_new=[]
        for json_data in json_array:

            if json_data["iudxResourceAPIs"]:
                if "TEMPORAL" in json_data["iudxResourceAPIs"]:
                    json_data["dataArrivalInterval"] = "Temporal"
                elif "TEMPORAL" not in json_data["iudxResourceAPIs"] and "ATTR" in json_data["iudxResourceAPIs"]:
                    json_data["dataArrivalInterval"] = "NonTemporal"



        # idss= ['461a8d17-028e-4f58-9c75-d419c16f2655', '1c8bce59-02b1-4a3e-9802-94bf5e6bdfe5', 'bef94acb-de2f-43a0-a04c-0abcf7306fd7', 'bc28db1f-6e75-43c9-b32e-2b162917eaa0', 'f914b2ac-001a-4988-a3ad-58e097ada439', 'fd7e7bc0-edba-4102-96ab-3b806cc9a159', '2dbca76b-b5c4-4f74-8eff-229c95275a5c', 'dd75d9e8-9d83-4aca-9c8f-10ee7b1ff84c', '1e73524c-eeb2-4e1c-a5b5-9aab649d2e82', 'd70d15bd-146e-46e9-b99f-1d87522b55e9', '47acc94b-e337-415d-a2cc-7cb054bfd6e4', '1424ad50-7c54-486e-893d-7c0aa64dc759', 'dc4b38c6-c51d-4601-929a-e89e1e6aadb9', '83749089-1abc-4115-98b3-024de9ac7fe6', '4e95367a-6c55-45b2-9197-d046733b6915', '53a3b8ff-8157-4f98-91ec-e23082de0b4d']
        # json_new=[]
        # for json_data in json_array:
        #     if json_data["id"] not in idss:

        #         if json_data.get("provider", None):
        #             print(json_data["id"])


                # if not json_data.get("itemCreatedAt", None):
                #     print(json_data["id"])

        #     if json_data["id"] not in idss:

        #         if not json_data.get("instance", None):

        #             ff = json_data["resourceGroup"]
        #             json_data["instance"] = requests.get(f"https://cos.iudx.org.in/iudx/cat/v1/item?id={ff}").json()["results"][0]["instance"]

        #         if not json_data.get("itemStatus", None):
        #             json_data["itemStatus"] = "active"

         
         
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

with open("../generated_data/extra-ri.jsonld", "w") as f:
    json.dump(uuid_data,f,indent=5)

print("done")

