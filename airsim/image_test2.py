import numpy as np
import airsim
import os
import cv2

client = airsim.VehicleClient()
client.confirmConnection()

filename = "test_uncompressed"
filename2= "test_compressed"
responses = client.simGetImages([airsim.ImageRequest("front_center", airsim.ImageType.Scene, False, False), 
                                 airsim.ImageRequest("front_center", airsim.ImageType.Scene, False, True)])

response = responses[0]
print(f"Len: {len(response.image_data_uint8)}, height: {response.height}, width: {response.width}")

# get numpy array
img1d = np.fromstring(response.image_data_uint8, dtype=np.uint8) 

# reshape array to 3 channel image array H X W X 3
img_rgb = img1d.reshape(response.height, response.width, 3)

# Display image for confirmation
cv2.imshow("Image", img_rgb)
cv2.waitKey(0)

# original image is fliped vertically
# img_rgb = np.flipud(img_rgb)

# write to png 
airsim.write_png(os.path.normpath(filename + '.png'), img_rgb)
# Write uncompressed image
# ret = cv2.imwrite(os.path.normpath(filename + '.png'), img_rgb)
# print(ret)

airsim.write_file(os.path.normpath(filename2 + '.png'), responses[1].image_data_uint8) 