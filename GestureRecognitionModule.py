import tensorflow as tf
import numpy as np


class GestureRecognizer:
    def __init__(self):
        self.model = tf.keras.models.load_model("model.h5")

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
