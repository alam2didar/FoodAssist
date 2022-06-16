# worker_handpos.py
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import DepthCameraModule as dcm
import HandDetectionModule as hdm
import DepthExtractionModule as dem
import GestureRecognitionModule as grm
import DepthContourFinderModule as dcfm
import ButtonPositionModule as bpm


class WorkerHandPos(QObject):
    # hand_position = {'x': 0, 'y': 0, 'z':0}
    finished = pyqtSignal()
    intReady = pyqtSignal(int, int, int, int)

# debug no camera
    # # Initialize Depth Camera Intel Realsense
    # depth_camera = dcm.DepthCamera()
# debug no camera

    # Initialize Hand Detector
    hand_detector = hdm.HandDetector()

    # Initialize DepthExtractor
    depth_extractor = dem.DepthExtractor()

    # Initialize Gesture Recognizer
    gesture_recognizer = grm.GestureRecognizer()

    # Initialize Gesture Recognizer
    depth_contour_finder = dcfm.DepthContourFinder()

    button_positioner = bpm.ButtonPositioner()

    worker_activated = True

    @pyqtSlot()
    def activate(self):
        self.worker_activated = True

    @pyqtSlot()
    def deactivate(self):
        self.worker_activated = False

    @pyqtSlot()
    def handPos(self): # A slot takes no params
        counter = 0
        while self.worker_activated:
            # increment counter
            counter = counter + 1

# debug no camera
            # # get images
            # # ret, depth_image, color_image = self.depth_camera.getFrame()
            # ret, depth_image, depth_colormap, color_image, bg_removed = self.depth_camera.getFrame()

            # # find point based on depth contour
            # point = self.depth_contour_finder.findPosition(depth_colormap)
            # # use knuckle coordinates to find distance
            # distance = int(self.depth_extractor.getHandPosition(point, depth_image, self.depth_camera)*1000)
            # # create hand_position object
            # hand_x, hand_y, hand_z = point[0], point[1], distance
# debug no camera

            # processing hand_x, hand_y to map into UI

            # resolution of UI
            # ui_res_x, ui_res_y = 1680, 1050

            # coordinates of the projected area
            # left_bottom_x, left_bottom_y = 600, 300
            # right_top_x, right_top_y = 1560, 840

            # mapped hand position into UI
            # hand_x = int(ui_res_x * (hand_x - left_bottom_x) / (right_top_x - left_bottom_x))
            # hand_y = int(ui_res_y - ui_res_y * (hand_y - left_bottom_y) / (right_top_y - left_bottom_y))

            # find hands
            # color_image, results = self.hand_detector.findHands(color_image)
            # find specified knuckle coordinates MIDDLE_FINGER_MCP
            # point = self.hand_detector.findPosition(color_image, results, targetId=9)
            # create detected_feature
            # gesture = self.gesture_recognizer.getRecognition(results, color_image)
            # dummy gesture
            # gesture = 0

# debug no camera
            # self.intReady.emit(hand_x, hand_y, hand_z, counter)
# debug no camera

        # finish upon breaking out of loop
        self.finished.emit()
