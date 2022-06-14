class DepthExtractor:
    def __init__(self):
        pass

    def getHandPosition(self, point, depth_image, depth_camera):
        distance = 0
        if point:
            # print(point)
            if (point[1] > 0) & (point[1] < depth_camera.color_height) & (point[0] < depth_camera.color_width) & (point[0] > 0):
                # find distance
                distance = depth_image[point[1], point[0]] * depth_camera.depth_scale
            else:
                # Out of bound
                distance = 0
        return distance
