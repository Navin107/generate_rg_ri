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
route = 'd0868f4a-be60-4a7b-affa-7bf6635c548a/.cdfe8a70-79d5-4631-bc52-0e80939d51ac'
ri_uuid = "cdfe8a70-79d5-4631-bc52-0e80939d51ac"
time_formatter = "%Y-%m-%dT%H:%M:%S+05:30"


class GandhinagarATCS(object):

    def getJunctionLocation(self):

        try:

            url = "https://125.21.250.180:7000/utmc/traffic_signal/static?page_num=1&page_len=50"

            payload = {}
            headers = {
            'auth-client': 'PSCL',
            'auth-licence': 'ccT0F804bU8093N3900I5ff4Sfe49Ob58aS3b'
            }

            response = requests.request("GET", url, headers=headers, data=payload, verify=False)

            self.transformData(response.json())


        except requests.Timeout as err:
            print("Connection Timeout error.")
        except requests.exceptions.ConnectionError:
            print("Connection refused.")
        except Exception as e:
            print("Exception occurred", e)

    def transformData(self, json_data):
        json_array = json_data["TrafficSignal"]["definitions"]
        print(json_array)
        transformOutput = []
        for packet in json_array:
            final_packet = {}
            final_packet['id']= ri_uuid
            final_packet["junctionID"] = packet["systemCodeNumber"]
            final_packet['junctionName']= packet["longDescription"]
            final_packet["location"] = {
                                        "type": "point",
                                        "coordinates": [float(packet["easting"]), float(packet["northing"])]
                                       }
            transformOutput.append(final_packet)

        self.deDuplication(transformOutput)



    def deDuplication(self, current_list_of_packets):
        
        """
        Removes duplicates from current_list of packets for each cycle &
        Stores list of packets seen in each cycle as json dump.
        :param current_list_of_packets: contains packets obtained at each cycle
        :type current_list_of_packets: List
        """

        if not(path.exists('../misc/prayagraj-atcs-junction.json')):
            with open('../misc/prayagraj-atcs-junction.json', 'w', encoding='utf-8') as fp:
                    
                    json.dump(current_list_of_packets, fp, indent=6)
                    self.publish_data(current_list_of_packets)

        else:
            with open('../misc/prayagraj-atcs-junction.json', 'r+', encoding='utf-8') as fp:
                    json_str = fp.read()

                    if json_str!="":
                        cache_list = json.loads(json_str)
                        fp.seek(0)
                        fp.truncate(0)
                        diff_list = [packet for packet in current_list_of_packets if packet not in cache_list]
                        json.dump(cache_list+diff_list, fp, indent=6)
                        self.publish_data(diff_list)

                    else:
                        
                        with open('../misc/prayagraj-atcs-junction.json', 'w', encoding='utf-8') as fp:
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
    sched.add_job(obj.getJunctionLocation, "interval", days=180)
    sched.start()

