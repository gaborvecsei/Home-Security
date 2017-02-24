import datetime
import threading
import time

import cv2

STATUS_STOPPED = 0
STATUS_RUNNING = 1


class HomeSecurity:
    def __init__(self, firebase, motion_detector, fps=10, camera_input_code=0):
        self.status = STATUS_STOPPED
        self.firebase = firebase
        self.camera_input_code = camera_input_code
        self.camera = None
        self.motion_detector = motion_detector
        self.fps = fps
        self.detection_thread = None

    def login(self, email, password, refresh_time_in_sec):
        succesful_login = self.firebase.authenticate(email, password)
        if succesful_login:
            self.refresh_user_authentication(refresh_time_in_sec)
        return succesful_login

    def refresh_user_authentication(self, time_in_sec):
        """
        We have to refresh our user because after 1 hour the authentication expires, so we need a new one
        This method
        :param time_in_sec: time to execute this function
        """

        self.firebase.refresh_user()
        print("User Token refreshed!")
        threading.Timer(time_in_sec, self.refresh_user_authentication, args=[time_in_sec]).start()

    def start_detection(self):
        self.camera = cv2.VideoCapture(self.camera_input_code)
        while self.status == STATUS_RUNNING:
            time_delta = 1. / self.fps
            time.sleep(time_delta)

            if self.status == STATUS_STOPPED:
                break

            ret, frame = self.camera.read()

            if not ret:
                print("No camera feed")
                continue

            debug_frame = frame.copy()

            is_detected, contour = self.motion_detector.detect(frame)

            if is_detected:
                frame_area = frame.shape[0] * frame.shape[1]
                contour_area = cv2.contourArea(contour)
                area_percentage = (contour_area / frame_area) * 100
                if area_percentage > 80:
                    continue
                print(
                    "Detected with area: {0:.2f} and image percentage: {1:.2f}%".format(contour_area, area_percentage))

                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(debug_frame, (x, y), (x + w, y + h), (0, 255, 0), 1)

                """*********************************
                *
                *       INSERT YOUR CODE HERE
                *
                * If you would like to use your own methods
                * (send email, play alarm sound, etc...), than call it here
                *********************************"""

                image_name = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f") + ".jpg"
                self.firebase.store_image(image_name, debug_frame)
        print("Detection ended!")

    def get_status_code(self):
        return self.status

    def stop(self):
        if self.detection_thread is not None and self.detection_thread.is_alive():
            self.status = STATUS_STOPPED
            self.camera.release()
            self.camera = None
            self.detection_thread = None

    def start(self):
        if self.detection_thread is None:
            self.status = STATUS_RUNNING
            self.detection_thread = threading.Thread(target=self.start_detection)
            self.detection_thread.start()
