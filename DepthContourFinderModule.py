import numpy as np
import imutils
import cv2


class DepthContourFinder:
    def __init__(self):
        pass

    def findPosition(self, depth_colormap):
        # new
        blur_image = cv2.GaussianBlur(depth_colormap, (5, 5), 0)
        hsv_image = cv2.cvtColor(blur_image, cv2.COLOR_BGR2HSV)
        mask2 = cv2.inRange(hsv_image, np.array([2, 0, 0]), np.array([20, 255, 255]))
        # kernel = np.ones((7, 7))
        kernel = np.ones((3, 3))
        dilation = cv2.dilate(mask2, kernel, iterations=1)
        erosion = cv2.erode(dilation, kernel, iterations=1)
        filtered = cv2.GaussianBlur(erosion, (5, 5), 0)
        # thresh_image = cv2.threshold(filtered, 0, 255, 0)[1]

        # Apply binary threshold using automatically selected threshold (using cv2.THRESH_OTSU parameter).
        # thresh_gray = cv2.threshold(thresh_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        thresh_gray = cv2.threshold(filtered, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        kernel = np.ones((5,5),np.uint8)
        # Use "opening" morphological operation for clearing some small dots (noise)
        # thresh_gray = cv2.morphologyEx(thresh_gray, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
        thresh_gray = cv2.morphologyEx(thresh_gray, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (40, 40)))
        thresh_gray = cv2.morphologyEx(thresh_gray, cv2.MORPH_OPEN, kernel)
        # Use "closing" morphological operation for closing small gaps
        # thresh_gray = cv2.morphologyEx(thresh_gray, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
        thresh_gray = cv2.morphologyEx(thresh_gray, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (30, 30)))
        thresh_gray = cv2.morphologyEx(thresh_gray, cv2.MORPH_CLOSE, kernel)

        cnts = cv2.findContours(thresh_gray.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        # initialize
        # right_hand_contour = None
        most_right_tip_x = 0
        most_right_tip_y = 0
        # offset for coordinates, using hand as cursor
        offset_x = -50
        offset_y = -100
        point = (0, 0)
        # loop over the contours
        for c in cnts:
            cX = tuple(c[c[:, :, 1].argmin()][0])[0]
            cY = tuple(c[c[:, :, 1].argmin()][0])[1]
            if cX > most_right_tip_x or cY > most_right_tip_y:
                most_right_tip_x = cX
                most_right_tip_y = cY
                # right_hand_contour = c
        if most_right_tip_x != 0 and most_right_tip_y != 0:
            point = (most_right_tip_x + offset_x, most_right_tip_y + offset_y)

        return point
