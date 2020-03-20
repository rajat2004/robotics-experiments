Scripts, files, etc. related to [AirSim](https://github.com/microsoft/AirSim)

* **high_res_camera.py**
    * Example script showing how to disable a camera.
    * It could be the case that a high-resolution camera is used infrequently, perhaps when some event is triggered. However, after using `simGetImages` once with the camera, the performance is severly affected.
    * Using `simDisableCamera` API, the camera can be disabled after the images have been taken, without any effect on the FPS
