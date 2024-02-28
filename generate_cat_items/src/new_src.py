import requests
import json

v = requests.get("https://cos.iudx.org.in/iudx/cat/v1/search?property=[instance]&value=[[hyderabad]]")
ff = v.json()["results"]
vvvv = []

rrrr=[]
item_val=None

for json_val in ff:
    if "iudx:Resource" in json_val["type"]:

        cc = json_val["resourceGroup"]

        json_val["provider"] = "9138727e-d868-484e-a601-3344de330736"
        json_val["ownerUserId"] = "98bd1444-96ef-421f-9661-e819ce867da7"
        json_val["cos"] = "637e32b6-9a6c-396f-914c-9db5d1a222b0"
        if json_val.get("iudxResourceAPIs", None):
            if "TEMPORAL" in json_val["iudxResourceAPIs"]:
                json_val["dataArrivalInterval"] = "Temporal"
            elif "TEMPORAL" not in json_val["iudxResourceAPIs"] and "ATTR" in json_val["iudxResourceAPIs"]:
                json_val["dataArrivalInterval"] = "NonTemporal"


        response = requests.get(f"https://cos.iudx.org.in/iudx/cat/v1/item?id={cc}")

        print(f"https://cos.iudx.org.in/iudx/cat/v1/item?id={cc}")
        if response.json()["results"][0].get("itemCreatedAt", None):
        
            json_val["itemCreatedAt"] = response.json()["results"][0]["itemCreatedAt"]

        else:
            json_val["itemCreatedAt"] = None


        desired_keys = [
            "@context", "id", "id_bck", "type",  "name", "label", "description", "tags", "accessPolicy", "apdURL",
            "provider", "provider_bck", "resourceServer", "resourceServer_bck",
            "resourceGroup", "resourceGroup_bck" ,  "resourceType",  "iudxResourceAPIs", "dataArrivalInterval",
            "dataDescriptor", "dataSample", "dataSampleFile", "location",
            "itemStatus", "instance", "ownerUserId", "cos", "itemCreatedAt"
        ]
        jj = {key: json_val[key] for key in desired_keys if json_val.get(key)}
        vvvv.append(jj)

    if "iudx:ResourceGroup" in json_val["type"]:
         
        desired_keys = [
                "@context", "type", "id", "name", "label", "description",
                "tags", "itemStatus", "provider", "location", "instance","ownerUserId", "cos", "itemCreatedAt"
            ]

        jjj = {key: json_val[key] for key in desired_keys if json_val.get(key)}
        rrrr.append(jjj)
 

with open("../generated_data/ri-item-new.json", "w") as f:
    json.dump(vvvv,f,indent=5)  

with open("../generated_data/rg-item.json", "w") as f:
    json.dump(rrrr,f,indent=5)    