import json
import os   


with open("D:/iudx/generate_rg_ri/generate_cat_items/generated_data/generate-resource-item-location-updated.jsonld", "r+") as json_file:
    f = json.load(json_file)




v=[i["instance"] for i in f]

x = set(v)
v = []

for i in f:

    id = i["id_bck"].split("/")[-1]
    city = i["instance"]

    # os.rmdir(f"D:/iudx/generate_rg_ri/generate_cat_items/uuid-master/{city}/resource-group")

    
    file_name = f"D:/iudx/generate_rg_ri/generate_cat_items/uuid-master/{city}/resource-item/{city}-{id}-ri.jsonld"
    # v.append(file_name)

    # try:
    #     os.remove(file_name)

    # except Exception as e:
    #     print(e)
    
    with open(file_name, 'w') as f:
        json.dump(i, f, indent=7)
        v.append(file_name)


print(len(v))


# [WinError 2] The system cannot find the file specified: 'D:/iudx/generate_rg_ri/generate_cat_items/uuid-master/bhubaneswar/resource-group/bhubaneswar-revenue-collection-ri.jsonld'
# [WinError 2] The system cannot find the file specified: 'D:/iudx/generate_rg_ri/generate_cat_items/uuid-master/bhubaneswar/resource-group/bhubaneswar-bike-docking-locations-ri.jsonld'
# [WinError 2] The system cannot find the file specified: 'D:/iudx/generate_rg_ri/generate_cat_items/uuid-master/bhubaneswar/resource-group/bhubaneswar-bike-docking-info-ri.jsonld'


