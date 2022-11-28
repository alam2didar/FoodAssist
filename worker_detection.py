# import datetime
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import cv2
import numpy as np

# Helper function
def zoom(img, zoom_factor=2):
    return cv2.resize(img, None, fx=zoom_factor, fy=zoom_factor)

# Creates WorkerDetection thread to run detection model
# sends the detection params and detected step
class WorkerDetection(QObject):
    finished = pyqtSignal()
    detection_params = pyqtSignal(int, int, int, int, int)
    worker_activated = True
    
    def __init__(self, depth_camera):
        super().__init__()
        self.depth_camera = depth_camera

    @pyqtSlot()
    def activate(self):
        self.worker_activated = True

    @pyqtSlot()
    def deactivate(self):
        self.worker_activated = False

    @pyqtSlot()
    def detect_step(self): # A slot takes no params
        while self.worker_activated:
            net = cv2.dnn.readNet('yolov3_final_final.weights', 'yolov3_final.cfg')
            #net = cv2.dnn.readNet('yolov3-tiny.weights', 'yolov3-tiny.cfg')
            classes = []
            #coco.names
            with open("classes.txt", "r") as f:
                classes = f.read().splitlines()
            
            font = cv2.FONT_HERSHEY_PLAIN
            colors = np.random.uniform(0, 255, size=(100, 3))
            # record_timestamp = datetime.datetime.now().strftime("%y%m%d%H%M%S")
            # record_camera_view = cv2.VideoWriter(f'camera_view_{record_timestamp}.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 4, (1920, 1080))
            while True:
                print('Capturing camera..')
                # get frames from depth camera and crop
                ret, _, _, img_original, _ = self.depth_camera.getFrame()
                y_size = img_original.shape[0]
                x_size = img_original.shape[1]
                centerY, centerX = int(y_size/2),int(x_size/2)
                cropped = img_original[centerY:y_size, 100:x_size-100]
                print("Cropped image shape: ", cropped.shape)
                # zoom image
                # img = zoom(img_temp, 3)
                img = zoom(cropped, 8)
                if not ret:
                    break
                height, width, _ = img.shape
                blob = cv2.dnn.blobFromImage(img, 1/255, (416, 416), (0,0,0), swapRB=True, crop=False)
                net.setInput(blob)
                output_layers_names = net.getUnconnectedOutLayersNames()
                layerOutputs = net.forward(output_layers_names)

                boxes = []
                confidences = []
                class_ids = []

                for output in layerOutputs:
                    for detection in output:
                        scores = detection[5:]
                        class_id = np.argmax(scores)
                        confidence = scores[class_id]
                        if confidence > 0.2:
                            center_x = int(detection[0]*width)
                            center_y = int(detection[1]*height)
                            w = int(detection[2]*width)
                            h = int(detection[3]*height)

                            x = int(center_x - w/2)
                            y = int(center_y - h/2)

                            boxes.append([x, y, w, h, center_x, center_y])
                            confidences.append((float(confidence)))
                            class_ids.append(class_id)

                indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.2, 0.4)

                if len(indexes)>0:
                    for i in indexes.flatten():
                        x, y, w, h, x3, y3 = boxes[i]
                        label = str(classes[class_ids[i]])
                        confidence = str(round(confidences[i],2))
                        color = colors[i]

                        # undo zoom and crop effect by reversing the calculation
                        pt1_x = int(x/8)+100
                        pt1_y = int(y/8)+centerY
                        pt1 = (pt1_x, pt1_y)
                        pt2_x = int((x+w)/8)+100
                        pt2_y = int((y+h)/8)+centerY
                        pt2 = (pt2_x, pt2_y)

                        self.detection_params.emit(pt1_x, pt1_y, int(w/8), int(h/8), class_ids[i]+1)

                        cv2.rectangle(img_original, pt1, pt2, color, 2)
                        cv2.putText(img_original, label + " " + confidence, (pt1_x, pt1_y+20), font, 2, (255,255,255), 2)
                else:
                    # if no detection, send box params (x,y,w,h) as 0
                    self.detection_params.emit(0, 0, 0, 0, 0)
                
                # record camera view
            #     record_camera_view.write(img_original)
            #     cv2.imshow('Detection Window', img_original)
            #     key = cv2.waitKey(1)
            #     if key==27:
            #         break

            # cv2.destroyAllWindows()


        # finish upon breaking out of loop
        self.finished.emit()
