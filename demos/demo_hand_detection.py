import DepthCameraModule as dcm
import HandDetectionModule as hdm
import DepthExtractionModule as dem
import GestureRecognitionModule as grm
import cv2

# Initialize Depth Camera Intel Realsense
depth_camera = dcm.DepthCamera()

# Initialize Hand Detector
hand_detector = hdm.HandDetector()

# Initialize DepthExtractor
depth_extractor = dem.DepthExtractor()

# Initialize Gesture Recognizer
gesture_recognizer = grm.GestureRecognizer()

while True:
    distance = None
    # get images
    ret, depth_image, depth_colormap, color_image, bg_removed = depth_camera.getFrame()
    # ret, depth_image, color_image = depth_camera.getFrame()
    # find hands
    color_image, results = hand_detector.findHands(color_image)
    # find specified knuckle coordinates MIDDLE_FINGER_MCP
    point = hand_detector.findPosition(color_image, results, targetId=9)
    # use knuckle coordinates to find distance
    if point:
        distance = depth_extractor.getHandPosition(point, depth_image, depth_camera)
        if distance:
            distance = int(distance*1000)

    # text_coordinates = str(point[0])+", "+str(point[1])+", "+str(distance)
    # "{:.2f}".format(distance)

    # create hand_position object
    if distance:
        hand_position = {'x': point[0], 'y': point[1], 'z': distance}
        print(hand_position)

    # create detected_feature
    # detected_feature = gesture_recognizer.getRecognition(results, color_image)
    # print(detected_feature)

    # cv2.putText(color_image, detected_feature, (10, 80), cv2.FONT_HERSHEY_PLAIN, 4, (255, 0, 255), 3)
    
    # cv2.putText(color_image, text_coordinates, (10, 1000), cv2.FONT_HERSHEY_PLAIN, 4, (255, 0, 255), 3)
    
    cv2.imshow("Image", color_image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print('User quits')
        break

# cv2.destroyAllWindows()
