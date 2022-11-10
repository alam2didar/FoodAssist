import mediapipe as mp
import cv2
import tensorflow as tf
import numpy as np


class HandDetector:
    def __init__(self, imgMode=False, maxHands=1):
        # initialize mediapipe
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(imgMode, maxHands)
        self.mpDraw = mp.solutions.drawing_utils
        # initialize tensorflow
        self.model = tf.keras.models.load_model("model.h5")
        # print("Initialized HandDetector.")

    def findHands(self, img, draw=False):
        if img is not None:
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.hands.process(imgRGB)
            # print(results.multi_hand_landmarks)
        if results.multi_hand_landmarks:
            for handLandmarks in results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLandmarks, self.mpHands.HAND_CONNECTIONS)
        return img, results

    def findPosition(self, img, results, targetId=0, handIndex=0):
        point = None
        if results.multi_hand_landmarks:
            selected_hand = results.multi_hand_landmarks[handIndex]
            for id, lm in enumerate(selected_hand.landmark):
                # print(id, lm, sep='\n')
                height, width, channel = img.shape
                cX, cY = int(lm.x * width), int(lm.y * height)
                if id == targetId:
                    point = (cX, cY)
        return point

    def getDistance(self, depth_camera, point, depth_image):
        distance = None
        if point:
            # print(point)
            if (point[1] > 0) & (point[1] < depth_camera.color_height) & (point[0] < depth_camera.color_width) & (point[0] > 0):
                # find distance
                distance = depth_image[point[1], point[0]] * depth_camera.depth_scale
        return distance

    def getRecognition(self, results, color_image):
        # FEATURE_LIST = ["Chop (feature 1)", "Vertical (feature 2)", "Flat (feature 3)"]
        detected_feature = 0
        if results.multi_hand_landmarks:
            input_buffer = []
            for handLandmarks in results.multi_hand_landmarks:
                for id, lm in enumerate(handLandmarks.landmark):
                    height, width, channel = color_image.shape
                    cX, cY = int(lm.x * width), int(lm.y * height)
                    # print(id, cX, cY)
                    # if id == 9:
                    #     print(id, cX, cY)
                    #     cv2.circle(img, (cX, cY), 20, (255, 0, 255), cv2.FILLED)
                    input_buffer.append(cX)
                    input_buffer.append(cY)
                # after enumeration
                input_array = np.array(input_buffer).reshape((-1, 42))
                # print(input_array)
                prediction = self.model.predict(input_array)
                # print(prediction)
                if prediction[0][0] > 0.5:
                    detected_feature = 1
                if prediction[0][1] > 0.5:
                    detected_feature = 2
                if prediction[0][2] > 0.5:
                    detected_feature = 3
        return detected_feature