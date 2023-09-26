import json
import requests
from collections import OrderedDict
import uuid

class IUDXDataProcessor:
    
    def __init__(self):
    
        self.resource_group_data = self.load_json_file('../raw/resourceGroup.json')
        self.resources_data = self.load_json_file('../raw/resources.json')
        self.provider_data = self.load_json_file('../raw/provider.json')
        self.user_data = self.load_json_file('../raw/sha-keycloak.json')
        self.resource_server_data = self.load_json_file("../raw/resource-server.json")

    def load_json_file(self, file_path):
        with open(file_path) as file:
            return json.load(file)

    def process_provider(self, json_data):
        provider_id = json_data["id"]

        json_data["id_bck"] = provider_id
        json_data["id"] = self.provider_data.get(provider_id)
        json_data["resourceServer"] = "ab311420-7d84-4a0a-9fdb-c811be588589"
        json_data["resourceServer_bck"] = "datakaveri.org/27e503da0bdda6efae3a52b3ef423c1f9005657a/rs.iudx.org.in"
        json_data["ownerUserId"] = self.user_data.get(provider_id)

        desired_keys = [
            "@context","id", "id_bck",  "type", "name", "description", "resourceServer", "resourceServer_bck", "providerOrg", "ownerUserId", "itemCreatedAt"
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

        if rg_id in ["vmc.gov.in/ae95ac0975a80bd4fd4127c68d3a5b6f141a3436/rs.iudx.org.in/vadodara-env-aqm", "datakaveri.org/facec5182e3bf44cc3ac42b0b611263676d668a2/rs.iudx.org.in/agartala-env-aqm", \
        "yulu.bike/8d3f8797db270e3c2f4a63aaa8b09bf63d66932b/rs.iudx.org.in/bhubaneswar-bike-docking-info"]:
            
            json_data.pop("dataSampleFile")


        desired_keys = ["@context", "id", "id_bck", "type", "name", "label", "description", "tags", "provider", "provider_bck", "itemStatus", "dataSampleFile", "location", "instance"]
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

        if not json_data.get("iudxResourceAPIs", None):
            if json_array[0].get("iudxResourceAPIs", None):
                json_data["iudxResourceAPIs"] = json_array[0].get("iudxResourceAPIs")

            else:
                print(ri_id)


        if not json_data.get("resourceType", None):
                if json_array[0].get("resourceType", None):
                    json_data["resourceType"] = json_array[0].get("resourceType")

                else:
                    print(ri_id)


        if rg_id in ["vmc.gov.in/ae95ac0975a80bd4fd4127c68d3a5b6f141a3436/rs.iudx.org.in/vadodara-env-aqm", "datakaveri.org/facec5182e3bf44cc3ac42b0b611263676d668a2/rs.iudx.org.in/agartala-env-aqm", \
        "yulu.bike/8d3f8797db270e3c2f4a63aaa8b09bf63d66932b/rs.iudx.org.in/bhubaneswar-bike-docking-info"]:
            
            
            json_data["dataSampleFile"] = json_array[0].get("dataSampleFile")

        desired_keys = [
            "@context", "id", "id_bck", "type",  "name", "label", "description", "tags", "accessPolicy", "apdURL",
            "provider", "provider_bck", "resourceServer", "resourceServer_bck",
            "resourceGroup", "resourceGroup_bck" ,  "resourceType",  "iudxResourceAPIs",
            "dataDescriptor", "dataSample", "dataSampleFile",
            "itemStatus", "instance"
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

        url = "https://api.catalogue.iudx.org.in/iudx/cat/v1/search?property=[type]&value=[[iudx:ResourceServer, iudx:ResourceGroup, iudx:Resource, iudx:Provider]]"
        json_array = self.fetch_url_data(url)

        json_changed_dict = []

        for json_data in json_array:

            json_data = OrderedDict(json_data)

            if "iudx:Provider" in json_data.get("type", []):
                if json_data["id"] in self.provider_data:
                    json_changed_dict.append(self.process_provider(json_data))

        return json_changed_dict

data_processor = IUDXDataProcessor()
uuid_data = data_processor.generate()

with open("../generated_data/generate-provider.jsonld", "w") as f:
    json.dump(uuid_data,f,indent=5)

print("done")