import mediapipe as mp
import cv2


class HandDetector:
    def __init__(self, imgMode=False, maxHands=1):
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(imgMode, maxHands)
        self.mpDraw = mp.solutions.drawing_utils
        # print("Initialized HandDetector.")

    def findHands(self, img, draw=True):
        if img is not None:
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.hands.process(imgRGB)
            # print(results.multi_hand_landmarks)
        if results.multi_hand_landmarks:
            for handLandmarks in results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLandmarks, self.mpHands.HAND_CONNECTIONS)
        return img, results

    def findPosition(self, img, results, targetId=0, handIndex=0, draw=True):
        point = (0, 0)
        if results.multi_hand_landmarks:
            selected_hand = results.multi_hand_landmarks[handIndex]
            for id, lm in enumerate(selected_hand.landmark):
                # print(id, lm, sep='\n')
                height, width, channel = img.shape
                cX, cY = int(lm.x * width), int(lm.y * height)
                if id == targetId:
                    point = (cX, cY)
                    # if draw:
                    #     cv2.circle(img, (cX, cY), 20, (255, 0, 255), cv2.FILLED)
                        # cv2.circle(img, (X1, Y1), (X2, Y2), 20, (255, 0, 0), 4)
        return point
