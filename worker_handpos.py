# worker_handpos.py
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import HandDetectionModule as hdm
import DepthExtractionModule as dem
import GestureRecognitionModule as grm
# import DepthContourFinderModule as dcfm
import ButtonPositionModule as bpm


class WorkerHandPos(QObject):
    # hand_position = {'x': 0, 'y': 0, 'z':0}
    finished = pyqtSignal()
    intReady = pyqtSignal(int, int, int, int, int, int)

    def __init__(self, my_depth_camera):
        super().__init__()
        # Initialize components
        self.hand_detector = hdm.HandDetector()
        self.depth_extractor = dem.DepthExtractor()
        self.gesture_recognizer = grm.GestureRecognizer()
        # self.depth_contour_finder = dcfm.DepthContourFinder()
        self.button_positioner = bpm.ButtonPositioner()
        self.depth_camera = my_depth_camera
        self.worker_activated = True

    @pyqtSlot()
    def activate(self):
        self.worker_activated = True

    @pyqtSlot()
    def deactivate(self):
        self.worker_activated = False

    @pyqtSlot()
    def handPos(self, use_mediapipe=True, use_depth_contour=False): # A slot takes no params
        counter = 0
        # while loop
        while self.worker_activated:
            counter = counter + 1
# debug no camera
            if self.depth_camera:
                # get images
                ret, depth_image, depth_colormap, color_image, bg_removed = self.depth_camera.getFrame()
                # alternative 1 - find point based on mediapipe
                color_image_to_process, results = self.hand_detector.findHands(color_image)
                # find specified knuckle coordinates INDEX_FINGER_TIP
                if use_mediapipe:
                    point = self.hand_detector.findPosition(color_image_to_process, results, targetId=8)
                # alternative 2 - find point based on depth contour
                # if not point and use_depth_contour:
                #     point = self.depth_contour_finder.findPosition(depth_colormap)
                # after finding point - use knuckle coordinates to find distance
                if point:
                    distance = self.depth_extractor.getHandPosition(point, depth_image, self.depth_camera)
                    if distance:
                        distance = int(distance*1000)
                        print("Hand position (x, y, z): ", (point[0], point[1], distance))
                        # only emit message with valid values
                        self.intReady.emit(point[0], point[1], distance, counter, int(1.65*(point[0]-405)-20), int(1.65*(point[1]-220)-20))
# debug no camera

        # finish upon breaking out of loop
        self.finished.emit()
