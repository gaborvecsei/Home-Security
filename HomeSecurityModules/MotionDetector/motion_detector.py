import threading

import cv2


class MotionDetector(object):
    def __init__(self, min_detection_area=100, kernel=(31, 31), sigma=0, background_image=None, refresh=False,
                 refresh_time=5):
        self.min_detection_area = min_detection_area
        k1, k2 = kernel
        if k1 % 2 == 0:
            k1 += 1
        if k2 % 2 == 0:
            k2 += 1
        self.kernel = (k1, k2)
        self.sigma = sigma

        self.prevImage = background_image
        self.original_image = None

        self.refresh_time = refresh_time

        if refresh:
            self.start_refreshing()

    def start_refreshing(self):
        self.prevImage = None
        threading.Timer(self.refresh_time, self.start_refreshing).start()

    def detect(self, image):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_image = cv2.equalizeHist(gray_image)
        blurred = cv2.GaussianBlur(gray_image, self.kernel, self.sigma)

        if self.prevImage is None:
            self.prevImage = blurred
        diff = cv2.absdiff(self.prevImage, blurred)
        _, binary = cv2.threshold(diff, 21, 255, cv2.THRESH_BINARY)

        if eval(cv2.__version__.split('.')[0]) == 3:
            _, cnts, hier = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        else:
            cnts, hier = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

        if len(cnts) < 1:
            is_detected = False
            contour = None
        else:
            largest_contour = cnts[0]
            if cv2.contourArea(largest_contour) < self.min_detection_area:
                is_detected = False
                contour = None
            else:
                is_detected = True
                contour = largest_contour
                self.prevImage = blurred
        return is_detected, contour

    def change_min_detection_area(self, min_area):
        self.min_detection_area = min_area
