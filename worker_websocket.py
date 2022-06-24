# worker_websocket.py
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import asyncio
import websockets
import json
import socket

# Creates a Websocket (Open for the entire duration when app is running)
# Smart watch communicates through this websocket
class WorkerWebsocket(QObject):
    websocket_finished = pyqtSignal()
    websocket_message = pyqtSignal(str, int)
    worker_activated = True
    wearable_transferring = False

    @pyqtSlot()
    def activate(self):
        self.worker_activated = True

    @pyqtSlot()
    def deactivate(self):
        self.worker_activated = False

    @pyqtSlot()
    def create_websocket(self): # A slot takes no params
        async def server(websocket, path):
            async for message in websocket:
                # print(message)
                if message == "start":
                    # start transfer signal
                    self.wearable_transferring = True
                    print("start transfer")
                elif message == "stop":
                    # stop transfer signal
                    self.wearable_transferring = False
                    print("stop transfer")
                else:
                    # json data transfer
                    try:
                        json_dict = json.loads(message)
                        # extract content from json
                        sensor_type = json_dict["type"]
                        if sensor_type == "position":
                            prob_0 = float(json_dict["prob_0"])
                            prob_1 = float(json_dict["prob_1"])
                            prob_2 = float(json_dict["prob_2"])
                            # pick out the highest probability
                            temp_max = max(prob_0, prob_1, prob_2)
                            if temp_max > 0.5:
                                # pick out result_feature
                                if prob_0 == temp_max:
                                    result_feature = 0
                                elif prob_1 == temp_max:
                                    result_feature = 1
                                elif prob_2 == temp_max:
                                    result_feature = 2
                                # emit result_type, result_feature (emitting gesture recognition from smart watch)
                                self.websocket_message.emit(sensor_type, result_feature)
                            else:
                                # no matching probability over 0.5 found
                                print("max value below 0.5: ", temp_max)
                        elif sensor_type == "motion":
                            # standard deviation of linear acceleration 
                            fused_sd = float(json_dict["prob_0"])
                            # emit result_type, fused_sd (emitting motion standard deviation from smart watch)
                            self.websocket_message.emit(sensor_type, fused_sd)
                    except json.JSONDecodeError:
                        print("invalid JSON")
        print("Preparing server...")
        # create new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # comment out to ignore server execution
        hostname=socket.gethostname()   
        ip_address=socket.gethostbyname(hostname)   
        print(f'IP Address: {ip_address}') 
        
        self.start_server = websockets.serve(server, ip_address, 5000)
        loop.run_until_complete(self.start_server)

        # comment out


        print("Server started ...")
        # asyncio.get_event_loop().run_forever()
        loop.run_forever()
        self.websocket_finished.emit()
