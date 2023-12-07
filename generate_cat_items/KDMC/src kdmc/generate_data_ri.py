import json
import requests
from collections import OrderedDict
import uuid

class IUDXDataProcessor:
    
    def __init__(self):
    
        self.resource_group_data = self.load_json_file('../raw_kdmc/resourceGroup.json')
        self.resources_data = self.load_json_file('../raw_kdmc/resources.json')
        self.provider_data = self.load_json_file('../raw_kdmc/provider.json')
        self.user_data = self.load_json_file('../raw_kdmc/sha-keycloak.json')
        self.resource_server_data = self.load_json_file("../raw_kdmc/resource-server-uuid.json")

    def load_json_file(self, file_path):
        with open(file_path) as file:
            return json.load(file)

    def process_resource(self, json_data):
        ri_id = json_data["id"]
        rg_id = json_data["resourceGroup"]
        provider_id = json_data["provider"]

        json_data["id_bck"] = ri_id
        json_data["id"] = self.resources_data.get(ri_id, {}).get("id")
        json_data["resourceServer"] = "274cf9f2-74b3-4f5c-8db2-7c4cad522a17"
        # json_data["resourceServer_bck"] = "datakaveri.org/27e503da0bdda6efae3a52b3ef423c1f9005657a/rs.iudx.org.in"
        json_data["resourceGroup"] = self.resource_group_data.get(rg_id) 
        json_data["resourceGroup_bck"] = rg_id
        json_data["provider"] = self.provider_data.get(provider_id)
        json_data["provider_bck"] = provider_id
        json_data["ownerUserId"] = self.user_data.get(provider_id)
        # json_data["cos"] =  "49f96c4c-e595-4fee-984c-43dededfba48"
        json_data["accessPolicy"] = "SECURE"
        json_data["apdURL"] = " "
        
        desired_keys = [
            "@context", "id", "id_bck", "type",  "name", "label", "description", "tags", "accessPolicy", "apdURL",
            "provider", "provider_bck", "resourceServer",
            "resourceGroup", "resourceGroup_bck" ,  "resourceType",  "adexResourceAPIs", "iudxResourceAPIs",
            "dataDescriptor", "dataSample", "location",
            "itemStatus", "instance", "ownerUserId", "cos", "itemCreatedAt"
        ]

        return self.extract_desired_keys(desired_keys, json_data)
    
    def fetch_url_data(self, url):
        response = requests.get(url)
        dict_data = response.json()
        json_array = dict_data.get("results", [])
        return json_array

    def extract_desired_keys(self, desired_keys, json_data):
        return {key: json_data[key] for key in desired_keys if json_data.get(key)}

    def generate(self):

        url = "https://kdmc.cop-nec.iudx.org.in/iudx/cat/v1/search?property=[type]&value=[[iudx:Resource]]"
        json_array = self.fetch_url_data(url)

        json_changed_dict = []

        for json_data in json_array:
            
            json_data = OrderedDict(json_data)
            json_changed_dict.append(self.process_resource(json_data))
    
        return json_changed_dict

data_processor = IUDXDataProcessor()
uuid_data = data_processor.generate()

with open("../generated_data/generate-resource-item.-kdmc.jsonld", "w") as f:
    json.dump(uuid_data,f,indent=5)

print("done")