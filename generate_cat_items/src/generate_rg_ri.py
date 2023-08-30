import json
import requests
from collections import OrderedDict

class IUDXDataProcessor:
    def __init__(self):
        self.data_files = {
            'resource_group_data': 'raw/resourceGroup.json',
            'resources_data': 'raw/resources.json',
            'provider_data': 'raw/sha-keycloak.json',
            'resource_server_data': 'raw/resource-server.json'
        }
        self.data = {key: self.load_json_file(file_path) for key, file_path in self.data_files.items()}

    def load_json_file(self, file_path):
        with open(file_path) as file:
            return json.load(file)

    def process_item(self, json_data, keys):
        processed_data = OrderedDict(json_data)
        for key, value in keys.items():
            processed_data[key] = value
        return processed_data

    def fetch_url_data(self, url):
        response = requests.get(url)
        dict_data = response.json()
        return dict_data.get("results", [])

    def generate(self):
        provider_url = "https://api.catalogue.iudx.org.in/iudx/cat/v1/list/provider"
        provider_list  = self.fetch_url_data(provider_url)
 
        url = "https://api.catalogue.iudx.org.in/iudx/cat/v1/search?property=[type]&value=[[iudx:ResourceServer, iudx:ResourceGroup, iudx:Resource, iudx:Provider]]"
        json_array = self.fetch_url_data(url)

        json_changed_dict = []
        final_dict = {}


        new_provider = []
        new_provider.extend(json_data["provider"] for json_data in json_array if "iudx:ResourceServer" in json_data.get("type", []) and json_data.get("provider", None) and json_data["provider"] not in provider_list and json_data["provider"] not in new_provider)
        provider_list.extend(new_provider)
        
        for provider in provider_list:
            json_changed_dict = []

            for json_data in json_array:
                json_data = OrderedDict(json_data)

                if ("iudx:Provider" in json_data.get("type", []) and json_data.get("id") == provider) or \
                ("iudx:ResourceGroup" in json_data.get("type", []) and json_data.get("provider") == provider) or \
                ("iudx:Resource" in json_data.get("type", []) and json_data.get("provider") == provider) or \
                ("iudx:ResourceServer" in json_data.get("type", []) and json_data.get("provider") == provider):
                    
                    if "iudx:Provider" in json_data.get("type", []) and json_data["id"] in self.provider_data:
                        json_changed_dict.append(self.process_provider(json_data))

                    if "iudx:ResourceServer" in json_data.get("type", []) and json_data["id"] in self.resource_server_data:
                        json_changed_dict.append(self.process_resource_server(json_data))  

                    if "iudx:ResourceGroup" in json_data.get("type", []) and json_data["id"] in self.resource_group_data:
                        json_changed_dict.append(self.process_resource_group(json_data))

                    if "iudx:Resource" in json_data.get("type", []) and json_data["id"] in self.resources_data:
                        json_changed_dict.append(self.process_resource(json_data))

            final_dict[provider] = json_changed_dict

        return final_dict

data_processor = IUDXDataProcessor()
uuid_data = data_processor.generate()

with open("generate_final.json", "w") as f:
    json.dump(uuid_data,f,indent=5)
