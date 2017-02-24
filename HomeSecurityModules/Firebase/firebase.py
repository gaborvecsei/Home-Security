import os

import cv2
import pyrebase
from requests.exceptions import HTTPError

TMP_FOLDER = "./tmp"
if not os.path.exists(TMP_FOLDER):
    os.mkdir(TMP_FOLDER)
    print("Tmp folder created")


class Firebase:
    def __init__(self, firebase_config):
        self.firebase = pyrebase.initialize_app(firebase_config)
        self.auth = self.firebase.auth()
        self.storage = self.firebase.storage()
        self.user = None
        self.user_info = None

    def authenticate(self, email, password):
        try:
            self.user = self.auth.sign_in_with_email_and_password(email, password)
            self.user_info = self.get_user_info()
            return True
        except HTTPError as e:
            print(e)
            return False

    def refresh_user(self):
        try:
            self.user = self.auth.refresh(self.user['refreshToken'])
            self.user_info = self.get_user_info()
            return True
        except Exception as e:
            print(e)
            return False

    def get_user(self):
        return self.user

    def get_user_id_token(self):
        return self.user['idToken']

    def get_user_info(self):
        return self.auth.get_account_info(self.user['idToken'])

    def store_image(self, image_name, image):
        image_path = os.path.join(TMP_FOLDER, image_name)
        cv2.imwrite(image_path, image)
        self.storage.child("security_images/" + image_name).put(image_path, self.get_user_id_token())
        os.remove(image_path)
