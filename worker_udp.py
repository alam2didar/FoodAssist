# Created by Youssef Elashry to allow two-way communication between Python3 and Unity to send and receive strings

# Feel free to use this in your individual or commercial projects BUT make sure to reference me as: Two-way communication between Python 3 and Unity (C#) - Y. T. Elashry
# It would be appreciated if you send me how you have used this in your projects (e.g. Machine Learning) at youssef.elashry@gmail.com

# Use at your own risk
# Use under the Apache License 2.0

# Example of a Python UDP server

import UdpComms as U
import time
import json
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

class WorkerUdp(QObject):
    udp_finished = pyqtSignal()
    current_step_update = pyqtSignal(int)
    result_requested = pyqtSignal(str)
    gesture_list = ["s1g1", "s2g1"]

    def __init__(self):
        super().__init__()
        # Create UDP socket to use for sending (and receiving)
        self.sock = U.UdpComms(udpIPServer="192.168.1.100", udpIPClient='192.168.1.102', portTX=8000, portRX=8001, enableRX=True, suppressWarnings=True)

    @pyqtSlot()
    def receive_message(self): # A slot takes no params
        while True:
            self.sock.SendDataToClient("Keep alive!")
            print("Keep alive!")
            
            message_received = self.sock.ReadReceivedData() # read data

            if message_received != None: # if NEW data has been received since last ReadReceivedData function call
                print(message_received)
                self.process_received_message('Received by Python: ' + str(message_received))

            time.sleep(1)

    @pyqtSlot()
    def process_received_message(self, data):
        # message_to_send = None
        # parse JSON string to dictionary
        try:
            # extract content from json string
            json_dict = json.loads(data)
            stage = json_dict["stage"]
            request_id = json_dict["request_id"]
            # emit signal update step
            self.current_step_update.emit(int(stage))
            # emit signal to request result
            self.result_requested.emit(request_id)
        except json.JSONDecodeError:
            print("invalid JSON")
            self.sock.SendDataToClient("invalid JSON")
        # case evaluation_finished
        # if message_to_send:
        #     self.has_message_to_send.emit(message_to_send)

    @pyqtSlot()
    def send_message(self, eval_error, response_id, gesture_score): # A slot takes no params
        # JSON data:
        x =  '{ }'
        # parsing JSON string:
        z = json.loads(x)
        # python object to be appended
        y = {"eval_error": eval_error,"response_id":response_id,"gesture_score":gesture_score}
        # appending the data
        z.update(y)
        # the result is a JSON string:
        json_string = json.dumps(z)
        # send json_string
        self.sock.SendDataToClient(json_string) # Send this string to other application
        print('Sent from Python: ' + json_string)
