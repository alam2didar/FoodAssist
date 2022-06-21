import pyrealsense2 as rs
import numpy as np
import cv2


class DepthCamera:
    def __init__(self):
        # configure depth and color streams
        self.pipeline = rs.pipeline()
        self.config = rs.config()

        # resolution has to 640 x 480, otherwise RuntimeError: Couldn't resolve requests
        self.depth_width = 1280
        self.depth_height = 720
        self.color_width = 1920
        self.color_height = 1080

        self.config.enable_stream(rs.stream.depth, self.depth_width, self.depth_height, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, self.color_width, self.color_height, rs.format.bgr8, 30)

        # start streaming
        self.profile = self.pipeline.start(self.config)
        print("Start streaming.")

        # adjust rgb color sensor
        # self.color_sensor = self.profile.get_device().first_color_sensor()
        # self.color_sensor.set_option(rs.option.enable_auto_exposure, False)
        # self.color_sensor.set_option(rs.option.auto_exposure_limit, 100)

        # getting the depth sensor's depth scale (see rs-align example for explanation)
        self.depth_sensor = self.profile.get_device().first_depth_sensor()
        self.depth_scale = self.depth_sensor.get_depth_scale()
        print("Depth Scale is: ", self.depth_scale)

        # declare sensor object and set options
        # self.depth_sensor.set_option(rs.option.visual_preset, 3)
        # 2 for no ambient light, 3 for low ambient light, 4 for max range , 5 for short range
        # self.depth_sensor.set_option(rs.option.confidence_threshold, 2)
        # self.depth_sensor.set_option(rs.option.noise_filtering, 6)

        # we will be removing the background of objects more than
        # clipping_distance_in_meters meters away
        clipping_distance_in_meters = 1  # 1 meter
        self.clipping_distance = clipping_distance_in_meters / self.depth_scale

        # create an align object
        # rs.align allows us to perform alignment of depth frames to others frames
        # the "align_to" is the stream type to which we plan to align depth frames.
        self.align_to = rs.stream.color
        self.align = rs.align(self.align_to)

    def getFrame(self):
        frames = self.pipeline.wait_for_frames()
        aligned_frames = self.align.process(frames)

        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()

        if not depth_frame or not color_frame:
            return False, None, None

        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # remove background - Set pixels further than clipping_distance to grey
        grey_color = 153
        depth_image_3d = np.dstack((depth_image, depth_image, depth_image)) # depth image is 1 channel, color is 3 channels
        bg_removed = np.where((depth_image_3d > self.clipping_distance) | (depth_image_3d <= 0), grey_color, color_image)

        # render images:
        # use COLORMAP_HSV color scheme
        # the greater alpha is, the shorter the focus is
        # depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        # depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.0262), cv2.COLORMAP_HSV)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.0234), cv2.COLORMAP_HSV)
        # calibrated alpha after distance change

        return True, depth_image, depth_colormap, color_image, bg_removed

    def release(self):
        self.pipeline.stop()
