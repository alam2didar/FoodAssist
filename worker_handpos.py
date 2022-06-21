# worker_handpos.py
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import HandDetectionModule as hdm
import DepthExtractionModule as dem
import GestureRecognitionModule as grm
import DepthContourFinderModule as dcfm
import ButtonPositionModule as bpm


class WorkerHandPos(QObject):
    # hand_position = {'x': 0, 'y': 0, 'z':0}
    finished = pyqtSignal()
    intReady = pyqtSignal(int, int, int)

    def __init__(self, my_depth_camera):
        super().__init__()
        # Initialize components
        self.hand_detector = hdm.HandDetector()
        self.depth_extractor = dem.DepthExtractor()
        self.gesture_recognizer = grm.GestureRecognizer()
        self.depth_contour_finder = dcfm.DepthContourFinder()
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
    def handPos(self): # A slot takes no params
        counter = 0
        # while loop
        while self.worker_activated:
            counter = counter + 1
# debug no camera
            # # get images
            # ret, depth_image, depth_colormap, color_image, bg_removed = self.depth_camera.getFrame()
            # # find point based on depth contour
            # point = self.depth_contour_finder.findPosition(depth_colormap)
            # # use knuckle coordinates to find distance
            # distance = int(self.depth_extractor.getHandPosition(point, depth_image, self.depth_camera)*1000)
            # # create hand_position object
            # hand_x, hand_y, hand_z = point[0], point[1], distance
            # self.intReady.emit(hand_x, hand_y, hand_z)
# debug no camera

        # finish upon breaking out of loop
        self.finished.emit()
