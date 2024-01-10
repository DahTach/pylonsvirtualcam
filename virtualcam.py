import argparse
import cv2

# import colorsys
import numpy as np
import pyvirtualcam
from pypylon import pylon

parser = argparse.ArgumentParser(description="Charta Scan")
parser.add_argument(
    "--show", default=False, action="store_true", help="show cv2 window preview"
)
parser.add_argument(
    "--vcam",
    default=False,
    action="store_true",
    help="stream to OBS virtual camera",
)
config = parser.parse_args()


class Camera:
    def __init__(self) -> None:
        self.first_device = pylon.TlFactory.GetInstance().CreateFirstDevice()
        self.cam = pylon.InstantCamera(self.first_device)
        self.cam.Open()
        self.cam.PixelFormat.Value = self.setColorSpace()
        self.converter = pylon.ImageFormatConverter()
        self.height = self.cam.Height.Max
        self.width = self.cam.Width.Max
        self.vcam = pyvirtualcam.Camera(width=self.width, height=self.height, fps=10)

    def startGrabbing(self):
        self.cam.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

    def setColorSpace(self):
        if config.show:
            return "BGR8"
        if config.vcam:
            return "RGB8"

    def setConverter(self):
        if config.show:
            # converting to opencv bgr format
            self.converter.OutputPixelFormat = pylon.PixelType_BGR8packed
            self.converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
        if config.vcam:
            self.converter.OutputPixelFormat = pylon.PixelType_RGB8packed
            self.converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

    def stream(self):
        while self.cam.IsGrabbing():
            grabResult = self.cam.RetrieveResult(
                5000, pylon.TimeoutHandling_ThrowException
            )

            if grabResult.GrabSucceeded():
                # Access the image data
                if config.show:
                    image = self.converter.Convert(grabResult)
                    self.show(image)
                if config.vcam:
                    image = self.converter.Convert(grabResult)
                    self.streamFake(image)
            grabResult.Release()

        # Releasing the resource
        self.cam.StopGrabbing()

    def show(self, image):
        img = image.GetArray()
        cv2.namedWindow("title", cv2.WINDOW_NORMAL)
        cv2.imshow("title", img)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            cv2.destroyAllWindows()

    def streamFake(self, frame):
        print(f"Using virtual camera: {self.vcam.device}")
        frame = frame.GetArray()
        self.vcam.send(frame)
        self.vcam.sleep_until_next_frame()


def main():
    cam = Camera()
    cam.startGrabbing()
    cam.setConverter()
    cam.stream()


if __name__ == "__main__":
    main()
