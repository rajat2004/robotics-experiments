import airsim
import numpy as np
import cv2
import tempfile
import os

'''
Simple script for testing image fetching with airsim

Settings used-

'''

client = airsim.VehicleClient()
client.confirmConnection()

tmp_dir = os.path.join(tempfile.gettempdir(), "airsim_simple_test")
print("Saving images to %s" % tmp_dir)
try:
    os.makedirs(tmp_dir)
except OSError:
    if not os.path.isdir(tmp_dir):
        raise

framecounter = 0

while True:
    responses = client.simGetImages([airsim.ImageRequest("front_center", airsim.ImageType.Scene, False, False),
                                    airsim.ImageRequest("front_center", airsim.ImageType.Scene, False, True)])
    response = responses[0]
    print(f"Len: {len(response.image_data_uint8)}, height: {response.height}, width: {response.width}")

    img1d = np.fromstring(response.image_data_uint8, dtype=np.uint8) # get numpy array
    img_rgb = img1d.reshape(response.height, response.width, 3) # reshape array to 3 channel image array H X W X 3
    # print(img_rgb)
    # print(img_rgb.dtype)
    cv2.imshow("Image", img_rgb)
    cv2.waitKey(1)

    print(response.image_data_uint8)
    filename = os.path.join(tmp_dir, str(framecounter)+"compress")
    # cv2.imwrite(os.path.normpath(filename + '.png'), img_rgb) # write to png
    framecounter+=1

    airsim.write_file(filename + '.png', response.image_data_uint8)
