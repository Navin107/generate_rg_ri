from datetime import date
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import requests
import json
import pytz
# from amqp import publish
exchange_to_publish = '6e9d6c91-7885-4faa-bb61-2406bb2bd354'
route = '6e9d6c91-7885-4faa-bb61-2406bb2bd354/.dadbc723-a369-4a85-9ed4-b630d06b3d43'
ri_uuid = "dadbc723-a369-4a85-9ed4-b630d06b3d43"
IST=pytz.timezone("Asia/Kolkata")

class ATCSVolume(object):

    def getToken(self, username, password):

        """
        :API is used to get token that we will use for get data.
        :GET method
        :param username:
        :param password:
        :return: token
        """
        data = '{ "username": "' + username + '","password": "' + password + '"}'
        response = requests.post(self.base_url + self.token_end_point, headers=self.headers, data=data)
        generatedToken = response.json()[0]["token"]
        return generatedToken

    def getData(self):

        """
        :Api is used for get vehicle pcu at each junction lane.
        :GET method
        :return:
        """

        try:
            url = "https://gscdlatcs.gandhinagarsmartcity.in/GN_ATCS/vehicleVolumes/online/city/Gandhinagar"

            payload = {}
            headers = {
                'Authorization': 'Basic QVRDUy1JQ0NDLVVTRVI6QVRDUy1JQ0NDLVVTRVJAMTIz'
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            city_data = response.json()["cityDetails"]["cityVolume"]

            self.transformData(city_data)
        except requests.Timeout as err:
            print("Connection Timeout error.")
        except requests.exceptions.ConnectionError:
            print("Connection refused.")
        except Exception as e:
            print("Exception occurred", e)

    def transformData(self, city_data):
        """
        :API is used to transform data according to our data model.
        :param city_data:
        :return: transformed all response data according to data model.
        """

        transformedOutput = []

        for packet in city_data:

            way_data = packet["JunctionVehicleVolume"]["wayVolume"]
            for i in range(len(way_data)):
                final_data = dict()
                final_data['id'] = "dadbc723-a369-4a85-9ed4-b630d06b3d43"
                final_data["junctionName"] = packet["JunctionVehicleVolume"]["junctionName"]
                way_data = packet["JunctionVehicleVolume"]["wayVolume"]
                final_data["roadName"] = way_data[i]["wayName"]
                final_data["pcu"] = way_data[i]["volume"]
                date_string = way_data[i]["lastUpdatedTime"]
                date_formats = ["%m/%d/%Y %I:%M:%S %p", "%d/%m/%Y %H:%M:%S"]
                for date_format in date_formats:
                    try:
                        datetime_obj = datetime.strptime(date_string, date_format)
                        break
                    except ValueError:
                        continue

                iudx_date_format = datetime_obj.astimezone(IST).isoformat()
                final_data["observationDateTime"] = iudx_date_format

                transformedOutput.append(final_data)

        self.deDuplicateAndPubllish(transformedOutput)

    def deDuplicateAndPubllish(self, transformedOutput):
        publishPackets = []

        for packet in transformedOutput:
            if packet["roadName"] not in atcs_cache:
                atcs_cache[packet["roadName"]] = packet["observationDateTime"]
                publishPackets.append(packet)
            elif packet["observationDateTime"] > atcs_cache[packet["roadName"]]:
                atcs_cache[packet["roadName"]] = packet["observationDateTime"]
                publishPackets.append(packet)

        # publish(exchange=exchange_to_publish, routing_key=route, message=json.dumps(publishPackets))
        print(json.dumps(publishPackets))


if __name__ == "__main__":
    sched = BlockingScheduler()
    obj = ATCSVolume()
    atcs_cache ={}
    obj.getData()

    sched.add_job(obj.getData, "interval", seconds=10)
    sched.start()
