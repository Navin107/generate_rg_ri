import requests
from datetime import date
from datetime import datetime
import requests
import json
from os import path
import dateutil.parser as dp

# from amqp import publish
from apscheduler.schedulers.blocking import BlockingScheduler


exchange_to_publish = 'd0868f4a-be60-4a7b-affa-7bf6635c548a'
route = 'd0868f4a-be60-4a7b-affa-7bf6635c548a/.9abe728d-b178-4691-bcb3-f89634e71c19'
ri_uuid = "9abe728d-b178-4691-bcb3-f89634e71c19"
time_formatter = "%Y-%m-%dT%H:%M:%S+05:30"


class GandhinagarATCS(object):

    def getJunctionLocation(self):

        try:
            url = "https://125.21.250.180:7000/utmc/transport_link/static?page_num=1&page_len=100&history=false"

            headers = {
            'auth-client': 'PSCL',
            'auth-licence': 'ccT0F804bU8093N3900I5ff4Sfe49Ob58aS3b'
            }

            response = requests.request("GET", url, headers=headers, verify=False)
            self.transformData(response.json())

        except requests.Timeout as err:
            print("Connection Timeout error.")
        except requests.exceptions.ConnectionError:
            print("Connection refused.")
        except Exception as e:
            print("Exception occurred", e)

    def transformData(self, json_data):
        json_array = json_data["TransportLink"]["definitions"]

        transformOutput = []

        for packet in json_array:
            final_packet = {}
            final_packet['id']= ri_uuid
            final_packet['roadID'] = packet["system_code_number"].split("_")[1]
            final_packet['roadName']= packet["transport_link_reference"]
            final_packet['carriagewayLength']= packet["link_distance"]            
            coordinates_packet = json.loads(packet["network_geom"])
            final_packet["location"] = coordinates_packet["coordinates"]

            transformOutput.append(final_packet)

        self.deDuplication(transformOutput)

    def deDuplication(self, current_list_of_packets):
        
        """
        Removes duplicates from current_list of packets for each cycle &
        Stores list of packets seen in each cycle as json dump.
        :param current_list_of_packets: contains packets obtained at each cycle
        :type current_list_of_packets: List
        """

        if not(path.exists('../misc/prayagraj-atcs-lane.json')):
            with open('../misc/prayagraj-atcs-lane.json', 'w', encoding='utf-8') as fp:
                    
                    json.dump(current_list_of_packets, fp, indent=6)
                    self.publish_data(current_list_of_packets)

        else:
            with open('../misc/prayagraj-atcs-lane.json', 'r+', encoding='utf-8') as fp:
                    json_str = fp.read()

                    if json_str!="":
                        cache_list = json.loads(json_str)
                        fp.seek(0)
                        fp.truncate(0)
                        diff_list = [packet for packet in current_list_of_packets if packet not in cache_list]
                        json.dump(cache_list+diff_list, fp, indent=6)
                        self.publish_data(diff_list)

                    else:
                        
                        with open('../misc/prayagraj-atcs-lane.json', 'w', encoding='utf-8') as fp:
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
    obj.getJunctionLocation()
    # sched.add_job(obj.getJunctionLocation, "interval", days=180)
    # sched.start()

