from PIL import Image
import cv2


class WebCam:
    logo = None
    show_logo = False
    flip = 2
    list = None

    FLIP_ORIGINAL = 2
    FLIP_HORIZONTAL = 1
    FLIP_VERTICAL = 0
    FLIP_HORIZONTAL_VERTICAL = -1

    def __init__(self, camera=0, size=None):
        self.camera = camera

        if not size:
            self.size = self.webcam_base
        else:
            self.size = size

        index = 0
        cam_list = []
        while True:
            cap = cv2.VideoCapture(index)
            if not cap.read()[0]:
                break
            else:
                cam_list.append(index)
            cap.release()
            index += 1

        self.list = cam_list
        self.cap = cv2.VideoCapture(self.camera)
        self.webcam_base = self._get_wecam_size()

    def get_frame(self):
        _, frame = self.cap.read()

        # Aplica flip
        if self.flip != self.FLIP_ORIGINAL:
            frame = cv2.flip(frame, self.flip)

        # Converte a cor do frame
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Transforma o array em imagem
        img = Image.fromarray(cv2image)

        # Reduz o tamanho da imagem
        img.thumbnail(self.size, reducing_gap=1.0)

        if self.show_logo and self.logo is not None:
            img.paste(self.logo, (2, 2), self.logo)

        return img

    def stop_cam(self):
        if self.cap.grab():
            self.cap.release()

    def open_cam(self):
        if not self.cap.grab():
            self.cap.open(0)

    def is_open(self):
        return self.cap.grab()

    def set_logo(self, path):
        try:
            self.logo = Image.open(path)
            self.logo.thumbnail((150, 30))
        except IOError:
            return False

        return True

    def change_camera(self, camera):
        self.cap = cv2.VideoCapture(camera)

    def _get_wecam_size(self):
        _, frame = self.cap.read()

        # Converte a cor do frame
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Transforma o array em imagem
        return Image.fromarray(cv2image).size
