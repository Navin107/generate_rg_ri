import requests
from datetime import date
from datetime import datetime
import requests
import json
from os import path
# from amqp import publish
from apscheduler.schedulers.blocking import BlockingScheduler

exchange_to_publish = '6e9d6c91-7885-4faa-bb61-2406bb2bd354'
route = '6e9d6c91-7885-4faa-bb61-2406bb2bd354/.8d002eca-84fa-467e-9409-45622b4525de'
ri_uuid = "8d002eca-84fa-467e-9409-45622b4525de"
time_formatter = "%Y-%m-%dT%H:%M:%S+05:30"


class GandhinagarATCS(object):
    
    def getLaneLocation(self):

        try:
            url = "https://gscdlatcs.gandhinagarsmartcity.in/GN_ATCS/CityDetails/gandhinagar"
            headers = {
            'Authorization': 'Basic QVRDUy1JQ0NDLVVTRVI6QVRDUy1JQ0NDLVVTRVJAMTIz'
            }
            response = requests.request("POST", url, headers=headers)
            self.transformData(response.json())

        except requests.Timeout as err:
            print("Connection Timeout error.")
        except requests.exceptions.ConnectionError:
            print("Connection refused.")
        except Exception as e:
            print("Exception occurred", e)

    def transformData(self, json_data):
        json_array = json_data["cityDetails"]

        transformOutput = []
        for packet in json_array:
            final_packet = {}
            final_packet['id']= ri_uuid
            final_packet['junctionName']= packet["junctionName"]
            for wayname_packet in packet["waynames"]:
                
                final_packet['roadName']= wayname_packet["WayName"]
                final_packet["location"] = wayname_packet["geometry"]
                transformOutput.append(final_packet)

        self.deDuplication(transformOutput)

    def deDuplication(self, current_list_of_packets):
        
        """
        Removes duplicates from current_list of packets for each cycle &
        Stores list of packets seen in each cycle as json dump.
        :param current_list_of_packets: contains packets obtained at each cycle
        :type current_list_of_packets: List
        """

        if not(path.exists('../misc/gandhinagar-atcs-lane-location.json')):
            with open('../misc/gandhinagar-atcs-lane-location.json', 'w', encoding='utf-8') as fp:
                    
                    json.dump(current_list_of_packets, fp, indent=6)
                    self.publish_data(current_list_of_packets)


        else:
            with open('../misc/gandhinagar-atcs-lane-location.json', 'r+', encoding='utf-8') as fp:
                    json_str = fp.read()

                    if json_str!="":
                        cache_list = json.loads(json_str)
                        fp.seek(0)
                        fp.truncate(0)
                        diff_list = [packet for packet in current_list_of_packets if packet not in cache_list]
                        json.dump(cache_list+diff_list, fp, indent=6)
                        self.publish_data(diff_list)

                    else:
                        
                        with open('../misc/gandhinagar-atcs-lane-location.json', 'w', encoding='utf-8') as fp:
                            json.dump(current_list_of_packets, fp, indent=6)
                            self.publish_data(current_list_of_packets)

    def publish_data(self, json_transformed_packet):

    
        for packet in json_transformed_packet:
            packet["observationDateTime"] = datetime.now().strftime(time_formatter)

            # publish(exchange=exchange_to_publish, routing_key=route, message=json.dumps(packet))
            print(json.dumps(packet, indent=4))

if __name__ == "__main__":
    sched = BlockingScheduler()
    obj = GandhinagarATCS()
    atcs_cache ={}
    obj.getLaneLocation()
    sched.add_job(obj.getLaneLocation, "interval", days=180)
    sched.start()

