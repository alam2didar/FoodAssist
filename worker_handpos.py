# worker_handpos.py
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import HandDetectionModule as hdm
import DepthContourFinderModule as dcfm
import ButtonPositionModule as bpm


class WorkerHandPos(QObject):
    finished = pyqtSignal()
    hand_position = pyqtSignal(int, int, int, int, int, int)
    vision_based_prob_message = pyqtSignal(str, float, float, float, float)

    def __init__(self, my_depth_camera):
        super().__init__()
        # Initialize components
        self.hand_detector = hdm.HandDetector()
        self.depth_contour_finder = dcfm.DepthContourFinder()
        self.button_positioner = bpm.ButtonPositioner()
        self.depth_camera = my_depth_camera
        self.worker_activated = True
        self.counter = 0

    @pyqtSlot()
    def reset_counter(self):
        self.counter = 0

    @pyqtSlot()
    def activate(self):
        self.worker_activated = True

    @pyqtSlot()
    def deactivate(self):
        self.worker_activated = False

    @pyqtSlot()
    def get_hand_position(self, use_mediapipe=True, use_depth_contour=True): # A slot takes no params
        # while loop
        while True:
            self.counter += 1
# debug no camera
            if self.depth_camera:
                # get images
                ret, depth_image, depth_colormap, color_image, bg_removed = self.depth_camera.getFrame()

                # alternative 1 - find point based on mediapipe
                # find specified knuckle coordinates
                if use_mediapipe:
                    color_image_to_process, results = self.hand_detector.findHands(color_image)
                    point = self.hand_detector.findPosition(color_image_to_process, results, targetId=12)
                    # potential keypoint model to predict gestures
                    vision_based_probs = self.hand_detector.getProbs(results, color_image_to_process)
                    prob_0, prob_1, prob_2, prob_3 = vision_based_probs[0], vision_based_probs[1], vision_based_probs[2], vision_based_probs[3]
                    # direct emission of probabilities
                    sensor_type = "vision"
                    self.vision_based_prob_message.emit(sensor_type, prob_0, prob_1, prob_2, prob_3)
                    # feature_label = self.hand_detector.getPrediction(results, color_image_to_process)
                    # print("Predicted gesture: " + feature_label)

                # alternative 2 - find point based on depth contour
                if not point and use_depth_contour:
                    point = self.depth_contour_finder.findPosition(depth_colormap)

                # after finding point - use knuckle coordinates to find distance
                if point:
                    distance = self.hand_detector.getDistance(self.depth_camera, point, depth_image)
                    if distance:
                        distance = int(distance*1000)
                        print("Hand position (x, y, z): ", (point[0], point[1], distance))
                        # only emit message with valid values
                        self.hand_position.emit(point[0], point[1], distance, self.counter, int(1.65*(point[0]-405)-20), int(1.65*(point[1]-220)-20))
# debug no camera

        # finish upon breaking out of loop
        self.finished.emit()
