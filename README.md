# pylonsvirtualcam
pypylons virtual cam via OBS virtual cam plugin

## 1. Install requirements
```
pip install -r requirements.txt
```
## 2. Install Obs with VIrtualCam Plugin


### For Linux:
```
sudo modprobe v4l2loopback devices=1 video_nr=21 card_label="VirtualWebCam"
```
