import DepthExtractionModule as dem
import DepthCameraModule as dcm
import numpy as np
import imutils
import cv2

# Initialize Camera Intel Realsense
depth_camera = dcm.DepthCamera()

# Initialize DepthExtractor
depth_extractor = dem.DepthExtractor()

while True:
    # get images
    ret, depth_image, depth_colormap, color_image, bg_removed = depth_camera.getFrame()

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

    # contours, hierarchy = cv2.findContours(depth_gray.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # sort contour in decreasing order
    # sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)

    # loop over the contours
    # for i, c in enumerate(sorted_contours[:3], 1):
    #     cv2.drawContours(color_image, c, i, (0, 255, 0), 3)
    #     cv2.putText(color_image, "center", (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # initialize
    right_hand_contour = None
    most_right_tip_x = 0
    most_right_tip_y = 0
    # loop over the contours
    for c in cnts:
        cX = tuple(c[c[:, :, 1].argmin()][0])[0]
        cY = tuple(c[c[:, :, 1].argmin()][0])[1]
        if cX > most_right_tip_x or cY > most_right_tip_y:
            most_right_tip_x = cX
            most_right_tip_y = cY
            right_hand_contour = c
        # compute the center of the contour
        # M = cv2.moments(c)
        # if M["m00"] != 0:
            # cX = int(M["m10"] / M["m00"])
            # cY = int(M["m01"] / M["m00"])
            # use tip of finger instead
            # cX = tuple(c[c[:, :, 1].argmin()][0])[0]
            # cY = tuple(c[c[:, :, 1].argmin()][0])[1]

        # # draw the contour and center of the shape on the image
        # img_contours = np.zeros(color_image.shape)
        # cv2.drawContours(color_image, c, -1, (0, 255, 0), 3)
        # # cv2.drawContours(color_image, [c], -1, (0, 255, 0), 2)
        # cv2.circle(color_image, (cX, cY), 7, (255, 255, 255), -1)
        # cv2.putText(color_image, "tip", (cX - 20, cY - 20),
        # cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    
    # draw the contour and center of the shape on the image
    img_contours = np.zeros(color_image.shape)
    cv2.drawContours(color_image, right_hand_contour, -1, (0, 255, 0), 3)
    # cv2.drawContours(color_image, [c], -1, (0, 255, 0), 2)
    # offset for coordinates, using hand as cursor
    offset_x = 15
    offset_y = 25
    if most_right_tip_x != 0 and most_right_tip_y != 0:
        cv2.circle(color_image, (most_right_tip_x + offset_x, most_right_tip_y + offset_y), 7, (255, 255, 255), -1)
    cv2.putText(color_image, "tip", (most_right_tip_x - 20, most_right_tip_y - 20),
    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    print((most_right_tip_x, most_right_tip_y))

    scale_percent = 200
    width = int(color_image.shape[1] * scale_percent / 100)
    height = int(color_image.shape[0] * scale_percent / 100)
    dim = (width, height)
    color_image = cv2.resize(color_image, dim, interpolation = cv2.INTER_AREA)
    depth_colormap = cv2.resize(depth_colormap, dim, interpolation = cv2.INTER_AREA)

    point = (0, 0)
    if most_right_tip_x != 0 and most_right_tip_y != 0:
        point = (most_right_tip_x + offset_x, most_right_tip_y + offset_y)
    # use knuckle coordinates to find distance
    distance = int(depth_extractor.getHandPosition(point, depth_image, depth_camera)*1000)

    # create hand_position object
    hand_position = {'x': point[0], 'y': point[1], 'z': distance}
    print(hand_position)

    # show the image
    cv2.imshow('depth_colormap', depth_colormap)
    cv2.imshow('color_image', color_image)
    # cv2.imshow('thresh_gray', thresh_gray)
    # cv2.imshow('thresh_image', thresh_image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print('User quits')
        break

cv2.destroyAllWindows()
