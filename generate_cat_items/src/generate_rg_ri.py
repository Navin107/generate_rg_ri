import json
import requests
from collections import OrderedDict
import uuid

class IUDXDataProcessor:
    
    def __init__(self):
    
        self.resource_group_data = self.load_json_file('../raw/resourceGroup.json')
        self.resources_data = self.load_json_file('../raw/resources.json')
        self.provider_data = self.load_json_file('../raw/sha-keycloak.json')
        self.resource_server_data = self.load_json_file("../raw/resource-server.json")

    def load_json_file(self, file_path):
        with open(file_path) as file:
            return json.load(file)

    def process_provider(self, json_data):
        provider_id = json_data["id"]

        json_data["id_bck"] = provider_id
        json_data["id"] = self.provider_data.get(provider_id)

        desired_keys = [
            "@context", "type", "id", "id_bck", "name", "description", "providerOrg"
        ]
        return self.extract_desired_keys(desired_keys, json_data)

    def process_resource_server(self, json_data):

        rs_id = json_data["id"]
        provider_id = json_data["provider"]

        json_data["id_bck"] = rs_id
        json_data["id"] = self.resource_server_data.get(rs_id)
        json_data["provider"] = self.provider_data.get(provider_id)
        json_data["provider_bck"] = provider_id
        desired_keys = [
            '@context', 'type', 'id', 'id_bck', 'provider', 'provider_bck','name', 
            'description', 'tags', 'resourceServerHTTPAccessURL', 
            'resourceServerStreamingAccessURL', 'resourceServerOrg', 
            'location', 'instance'
        ]
        return self.extract_desired_keys(desired_keys, json_data)
 
    def process_resource_group(self, json_data):
        rg_id = json_data["id"]
        provider_id = json_data["provider"]

        json_data["id_bck"] = rg_id
        json_data["id"] = self.resource_group_data.get(rg_id) 
        json_data["provider"] = self.provider_data.get(provider_id)
        json_data["provider_bck"] = provider_id

        desired_keys = [
            "@context", "type", "id", "id_bck", "name", "label", "description",
            "tags", "itemStatus", "provider", "provider_bck", 
            "resourceType", "iudxResourceAPIs", "location", "instance"
        ]
        return self.extract_desired_keys(desired_keys, json_data)
    
    def process_resource(self, json_data):
        ri_id = json_data["id"]
        rg_id = json_data["resourceGroup"]
        provider_id = json_data["provider"]

        json_data["id_bck"] = ri_id
        json_data["id"] = self.resources_data.get(ri_id, {}).get("id")
        json_data["resourceServer"] = "ab311420-7d84-4a0a-9fdb-c811be588589"
        json_data["resourceServer_bck"] = "datakaveri.org/27e503da0bdda6efae3a52b3ef423c1f9005657a/rs.iudx.org.in"
        json_data["resourceGroup"] = self.resource_group_data.get(rg_id) 
        json_data["resourceGroup_bck"] = rg_id
        json_data["provider"] = self.provider_data.get(provider_id)
        json_data["provider_bck"] = provider_id

        url = "https://api.catalogue.iudx.org.in/iudx/cat/v1/item?id={}".format(json_data["resourceGroup_bck"])
        json_array = self.fetch_url_data(url)

        json_data["accessPolicy"] = json_array[0]["accessPolicy"]
        json_data["apdURL"] = "acl-apd.iudx.org.in"

        desired_keys = [
            "@context", "type", "id", "id_bck", "name", "label",
            "description", "resourceServer", "resourceServer_bck", "tags", "dataSampleFile",
            "itemStatus", "resourceGroup", "resourceGroup_bck",
            "provider", "provider_bck", "resourceType", "accessPolicy",
            "apdURL", "iudxResourceAPIs", "dataDescriptor",
            "dataSample", "instance"
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


        rg_url = "https://api.catalogue.iudx.org.in/iudx/cat/v1/list/resourceGroup"
        rg_list  = self.fetch_url_data(rg_url)
 
        url = "https://api.catalogue.iudx.org.in/iudx/cat/v1/search?property=[type]&value=[[iudx:ResourceGroup, iudx:Resource]]"

        json_array = self.fetch_url_data(url)

        json_changed_dict = []
        final_dict = {}



        for resourceGroup in rg_list:
            json_changed_dict = []

            for json_data in json_array:

                json_data = OrderedDict(json_data)


                if ("iudx:ResourceGroup" in json_data.get("type", []) and json_data.get("id") == resourceGroup) or ("iudx:Resource" in json_data.get("type", []) and json_data.get("resourceGroup") == resourceGroup): 
                    

      
                    if "iudx:ResourceGroup" in json_data.get("type", []):
                        if json_data["id"] in self.resource_group_data:
                            json_changed_dict.append(self.process_resource_group(json_data))
      

     
                    if "iudx:Resource" in json_data.get("type", []):
                        if json_data["id"] in self.resources_data:
                            json_changed_dict.append(self.process_resource(json_data))
           

           

            final_dict[resourceGroup] = json_changed_dict



        return final_dict

data_processor = IUDXDataProcessor()
uuid_data = data_processor.generate()
with open("../generated_data/generate-rg-ri.json", "w") as f:
    json.dump(uuid_data,f,indent=5)