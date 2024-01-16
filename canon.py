import argparse
import cv2
import atexit
import sys

# import pyvirtualcam
import numpy as np
import io
import gphoto2 as gp
import logging as log

parser = argparse.ArgumentParser(description="Charta Scan")
parser.add_argument(
    "--debug", default=False, action="store_true", help="show cv2 window preview"
)
parser.add_argument(
    "--backend",
    choices=["v4l2loopback", "obs", "unitycapture"],
    default="v4l2loopback",
    help="choose system related backend",
)
parser.add_argument(
    "--device",
    choices=["/dev/video<n>", "OBS Virtual Camera", "Unity Video Capture"],
    default="/dev/video21",
    help="choose system related backend device",
)
config = parser.parse_args()

log.basicConfig(format="%(levelname)s: %(name)s: %(message)s", level=log.WARNING)


callback_obj = gp.check_result(gp.use_python_logging())
camera = gp.check_result(gp.gp_camera_new())
gp.check_result(gp.gp_camera_init(camera))
# required configuration will depend on camera type!
print("Checking camera config")
# get configuration tree
config = gp.check_result(gp.gp_camera_get_config(camera))


class Camera:
    def __init__(self, camera, config):
        self.cam = camera
        self.config = config
        # self.vcam = pyvirtualcam.Camera(
        #     width=self.config.width,
        #     height=self.config.height,
        #     fps=10,
        #     device=config.device,
        #     backend=config.backend,
        # )
        self.atexit = atexit.register(self._exit_handler)

    def _exit_handler(self):
        # print(f"Closing vcam {self.vcam}")
        # self.vcam.close()
         self.cam.exit()

    def init(self):
        try:
            # self.device = gp.Camera()
            # self.device = gp.gp_camera_new()
            self.cam = gp.gp_camera_init(self.device)
        except Exception:
            raise Exception(
                f"Could not initialize device {self.device} as camera {self.cam}:\n{Exception}"
            )

    def get_config(self):
        try:
            config = gp.gp_camera_get_config(self.cam)
            return config
        except Exception:
            log.warning(f"Could not get config of camera {self.cam}:\n{Exception}")

    def stream(self):
        preview = self.cam.capture_preview()
        filedata = preview.get_data_and_size()
        data = memoryview(filedata)
        stream = io.BytesIO(filedata)
        return stream

    def streamFake(self, frame):
        print(f"Using virtual camera: {self.vcam.device}")
        frame = frame.GetArray()
        self.vcam.send(frame)
        self.vcam.sleep_until_next_frame()

    def show_stream(self, stream):
        frame = cv2.imdecode(np.frombuffer(stream.read(), np.uint8), 1)
        cv2.imshow(f"capture {self.cam}", frame)

        # def capture(self):
        #    img_path = self.cam.capture(gp.GP_CAPTURE_IMAGE)
        #    print("Camera file path: {0}/{1}".format(img_path.folder, img_path.name))
        #    img_file = self.cam.file_get(
        #        img_path.folder, img_path.name, gp.GP_FILE_TYPE_NORMAL
        #    )
        #    # image = cv2.imread(img_path)
        #    image = cv2.imread(img_file)
        #    self.show(image)
        #    return image

    def capture(self):
        img_path = self.cam.capture(gp.GP_CAPTURE_IMAGE)
        img_file = self.cam.file_get(
            img_path.folder, img_path.name, gp.GP_FILE_TYPE_NORMAL
        )
        filedata = img_file.get_data_and_size()
        data = memoryview(filedata)
        frame_data = io.BytesIO(filedata)
        image = cv2.imdecode(np.frombuffer(frame_data.read(), np.uint8), 1)
        cv2.imshow('Capture', image)
        cv2.waitKey(0)


    def pippi(self):
        key = 0
        while key != ord("q"):
            stream = self.stream()
            self.show_stream(stream)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("c"):
                self.capture()
        cv2.destroyAllWindows()


def main():
    cam = Camera(camera, config)
    cam.pippi()


if __name__ == "__main__":
    sys.exit(main())
