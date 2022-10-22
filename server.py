# Created by Youssef Elashry to allow two-way communication between Python3 and Unity to send and receive strings

# Feel free to use this in your individual or commercial projects BUT make sure to reference me as: Two-way communication between Python 3 and Unity (C#) - Y. T. Elashry
# It would be appreciated if you send me how you have used this in your projects (e.g. Machine Learning) at youssef.elashry@gmail.com

# Use at your own risk
# Use under the Apache License 2.0

# Example of a Python UDP server

import UdpComms as U
import time
import json

# Create UDP socket to use for sending (and receiving)
sock = U.UdpComms(udpIPServer="192.168.65.40", udpIPClient='192.168.71.170', portTX=8000, portRX=8001, enableRX=True, suppressWarnings=True)
i = 0

# sock.SendDataToClient("") # Send this string to other application
# i += 1
# print('Sent from Python: ' + str(i))

while True:
    sock.SendDataToClient(str(i)) # Send this string to other application
    i += 1
    print('Sent from Python: ' + str(i))
    
    data = sock.ReadReceivedData() # read data

    if data != None: # if NEW data has been received since last ReadReceivedData function call
        print(data) # print new received data
        # sock.SendDataToClient("Received!")
        try:
            # extract content from json string
            json_dict = json.loads(data)
            stage = json_dict["stage"]
            request_id = json_dict["request_id"]
            if stage == "0" and request_id == "-1":
                print('requested evaluation')
                pass
            elif stage == "-1" and request_id == "s1g1":
                # JSON data:
                x =  '{ }'
                # parsing JSON string:
                z = json.loads(x)
                # python object to be appended
                y = {"eval_error": -1,"response_id":"s1g1","gesture_score":20,"worst_gesture":-1}
                # appending the data
                z.update(y)
                # the result is a JSON string:
                json_string = json.dumps(z)
                # send json_string
                sock.SendDataToClient(json_string) # Send this string to other application
                print('Sent from Python: ' + json_string)
        except json.JSONDecodeError:
            print("invalid JSON")

    time.sleep(1)
