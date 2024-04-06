import json
import os
import subprocess
import time
import regex as re
import requests

def get_tripIDs():
    url = f"https://hackhpi24.ivo-zilkenat.de/api/trips/"
    #url = f"http://localhost:3001/api/trips/"
    data = {"bounds": {"upper-left": {"lat": 40.7128,"lon": -74.006}, "lower-right": {"lat": 40.7128,"lon": -74.006}}}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json().keys()
    else:
        print(f"Failed to get data, status code: {response.status_code}")

# open watch stream
VIDEO_ID = os.environ['VID']
TOTAL_CAPACITY = 50
# REDIS_HOST = 'vm-testing-iz.cloud.dhclab.i.hpi.de'
REDIS_HOST = 'localhost'
# Read port from environment variable
REDIS_PORT = os.environ['REDIS_PORT']
p = subprocess.Popen(['python3', '/root/starwit-fork/tools/echo.py', '-s', 'objecttracker:stream1', '--redis-host', REDIS_HOST, '--redis-port', REDIS_PORT], stdout=subprocess.PIPE)
# constantly read from stream
frame: str = ""

# start a timer, average the number of detections over a second
begin_average = time.time()
num_detections = []

while True:
    line = p.stdout.readline().decode()
    if not line:
        break
    frame += line

    if(re.match('^}\\s*$', line)):
        # deserialize line into object
        json_data = json.loads(frame)
        frame = ""
        if 'detections' not in json_data:
            num_detections.append(0)
        else:
            num_detections.append(len(json_data['detections']))

        # calculate average detections per second
        if time.time() - begin_average > 10:
            max_detections = max(num_detections)
            print("Highest number of detections in a second (is sent to server): ", max(num_detections))
            # print number of detections which was detected the most
            # this is useful as passengers outside the vehicle are not detected
            print("Most detected number of detections: ", max(set(num_detections), key = num_detections.count))

            vehicles = get_tripIDs()
            for i in range(len(vehicles)):
                if i % VIDEO_ID == 0:
                    trip_id = vehicles[i]
                    # Send packet to backend, HTTP Post
                    print(requests.post(f'https://hackhpi24.ivo-zilkenat.de/api/trips/{trip_id}/updateUtilization', json={"abs": max_detections, "rel": max_detections / TOTAL_CAPACITY}))

            num_detections = []
            begin_average = time.time()
