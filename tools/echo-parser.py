import json
import subprocess
import time
import regex as re
import requests

# open watch stream
TRIP_ID = 1
TOTAL_CAPACITY = 50
REDIS_HOST = 'vm-testing-iz.cloud.dhclab.i.hpi.de'
#REDIS_HOST = 'localhost'
REDIS_PORT = '10003'
p = subprocess.Popen(['python3', 'echo.py', '-s', 'objecttracker:stream1', '--redis-host', REDIS_HOST, '--redis-port', REDIS_PORT], stdout=subprocess.PIPE)
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
            print("Highest number of detections in a second: ", max(num_detections))
            # print number of detections which was detected the most
            # this is useful as passengers outside the vehicle are not detected
            print("Most detected number of detections: ", max(set(num_detections), key = num_detections.count))
            # Send packet to backend, HTTP Post
            print(requests.post(f'https://hackhpi24.ivo-zilkenat.de/api/{TRIP_ID}/updateUtilization', json={"abs": max_detections, "rel": max_detections / TOTAL_CAPACITY}))

            num_detections = []
            begin_average = time.time()
