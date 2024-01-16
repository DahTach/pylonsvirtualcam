import argparse
import cv2
import atexit
import pyvirtualcam
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


class Camera:
    def __init__(self):
        self.device = gp.Camera()
        self.cam = self.device.init()
        self.config = self.get_config
        self.vcam = pyvirtualcam.Camera(
            width=self.config.width,
            height=self.config.height,
            fps=10,
            device=config.device,
            backend=config.backend,
        )
        self.atexit = atexit.register(self._exit_handler)

    def _exit_handler(self):
        print(f"Closing vcam {self.vcam}")
        self.vcam.close()
        self.cam.exit()

    def init_camera(self):
        try:
            camera = self.device.init()
            return camera
        except Exception:
            raise Exception(f"Could not initialize device {self.device}:\n{Exception}")

    def get_config(self):
        try:
            config = gp.gp_camera_get_config(self.cam)
            return config
        except Exception:
            log.warning(f"Could not get config of camera {self.cam}:\n{Exception}")

    def stream(self):
        while True:
            preview = self.cam.capture_preview()
            filedata = preview.get_data_and_size()
            data = memoryview(filedata)
            print(type(data), len(data))
            print(data[:10].tolist())
            stream = io.BytesIO(filedata)
            frame = cv2.imdecode(np.frombuffer(stream.read(), np.uint8), 1)
            if config.show:
                self.show(frame)
            return frame
        self.cam.exit()

    def streamFake(self, frame):
        print(f"Using virtual camera: {self.vcam.device}")
        frame = frame.GetArray()
        self.vcam.send(frame)
        self.vcam.sleep_until_next_frame()

    def show(self, frame):
        key = 0
        while key != ord("q"):
            cv2.imshow(f"Streaming {self.cam}", frame)
            key = cv2.waitKey(0) & 0xFF
        cv2.destroyAllWindows()

    def capture(self):
        img_path = self.cam.capture(gp.GP_CAPTURE_IMAGE)
        print("Camera file path: {0}/{1}".format(img_path.folder, img_path.name))
        img_file = self.cam.file_get(
            img_path.folder, img_path.name, gp.GP_FILE_TYPE_NORMAL
        )
        # image = cv2.imread(img_path)
        image = cv2.imread(img_file)
        self.show(image)
        return image


def main():
    cam = Camera()
    cam.stream()


if __name__ == "__main__":
    main()
