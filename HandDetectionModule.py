import mediapipe as mp
import cv2
import csv
import copy
import itertools
from keypoint_classifier.keypoint_classifier import KeyPointClassifier


class HandDetector:
    def __init__(self, imgMode=False, maxHands=1):
        # initialize mediapipe
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(imgMode, maxHands)
        self.mpDraw = mp.solutions.drawing_utils
        # load model
        self.keypoint_classifier = KeyPointClassifier()
        # read labels
        with open('model/keypoint_classifier/keypoint_classifier_label.csv',
                encoding='utf-8-sig') as f:
            self.keypoint_classifier_labels = csv.reader(f)
            self.keypoint_classifier_labels = [
                row[0] for row in self.keypoint_classifier_labels
            ]
        # print("Initialized HandDetector.")


    def findHands(self, img):
        if img is not None:
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.hands.process(imgRGB)
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


    def getPrediction(self, results, color_image):
        if results.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                # Landmark calculation
                landmark_list = self.calc_landmark_list(color_image, hand_landmarks)
                # Conversion to relative coordinates / normalized coordinates
                pre_processed_landmark_list = self.pre_process_landmark(landmark_list)
                # Hand sign classification
                hand_sign_id = self.keypoint_classifier(pre_processed_landmark_list)
                # feature label
                feature_label = self.keypoint_classifier_labels[hand_sign_id]
        return feature_label


    def calc_landmark_list(image, landmarks):
        image_width, image_height = image.shape[1], image.shape[0]

        landmark_point = []

        # Keypoint
        for _, landmark in enumerate(landmarks.landmark):
            landmark_x = min(int(landmark.x * image_width), image_width - 1)
            landmark_y = min(int(landmark.y * image_height), image_height - 1)
            # landmark_z = landmark.z

            landmark_point.append([landmark_x, landmark_y])

        return landmark_point


    def pre_process_landmark(landmark_list):
        temp_landmark_list = copy.deepcopy(landmark_list)

        # Convert to relative coordinates
        base_x, base_y = 0, 0
        for index, landmark_point in enumerate(temp_landmark_list):
            if index == 0:
                base_x, base_y = landmark_point[0], landmark_point[1]

            temp_landmark_list[index][0] = temp_landmark_list[index][0] - base_x
            temp_landmark_list[index][1] = temp_landmark_list[index][1] - base_y

        # Convert to a one-dimensional list
        temp_landmark_list = list(
            itertools.chain.from_iterable(temp_landmark_list))

        # Normalization
        max_value = max(list(map(abs, temp_landmark_list)))

        def normalize_(n):
            return n / max_value

        temp_landmark_list = list(map(normalize_, temp_landmark_list))

        return temp_landmark_list
