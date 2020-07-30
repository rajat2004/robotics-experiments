from argparse import ArgumentParser
import airsim
import time
import threading
import numpy as np
import cv2
import tempfile
import os

cameraTypeMap = { 
    "depth": airsim.ImageType.DepthVis,
    "segmentation": airsim.ImageType.Segmentation,
    "seg": airsim.ImageType.Segmentation,
    "scene": airsim.ImageType.Scene,
    "disparity": airsim.ImageType.DisparityNormalized,
    "normals": airsim.ImageType.SurfaceNormals
}

def saveImage(response, filename):
    if response.pixels_as_float:
        print(f"""Type {response.image_type}, size {len(response.image_data_float)}, "
                  height {response.height}, width {response.width}""")
        # airsim.write_pfm(os.path.normpath(filename + '.pfm'), airsim.get_pfm_array(response))
        depth = np.array(response.image_data_float, dtype=np.float64)
        depth = depth.reshape(response.height, response.width, -1)
        depth = np.array(depth * 255, dtype=np.uint8)
        # save pic
        cv2.imwrite('{}.png'.format(filename), depth)
    elif response.compress: #png format
        print("Type %d, size %d, height %d, width %d" % (response.image_type, len(response.image_data_uint8),
                response.height, response.width))
        airsim.write_file(os.path.normpath(filename + '.png'), response.image_data_uint8)
    else: #uncompressed array
        print(f"""Type {response.image_type}, size {len(response.image_data_uint8)}, "
                  height {response.height}, width {response.width}""")
        img1d = np.fromstring(response.image_data_uint8, dtype=np.uint8) # get numpy array
        img_rgb = img1d.reshape(response.height, response.width, 3) # reshape array to 3 channel image array H X W X 3
        cv2.imwrite(os.path.normpath(filename + '.png'), img_rgb) # write to png

class ImageBenchmarker():
    def __init__(self, 
            img_benchmark_type = 'simGetImages', 
            viz_image_cv2 = False,
            save_images = False,
            img_type = "scene"):
        self.airsim_client = airsim.VehicleClient()
        self.airsim_client.confirmConnection()
        self.image_benchmark_num_images = 0
        self.image_benchmark_total_time = 0.0
        self.image_callback_thread = None
        self.viz_image_cv2 = viz_image_cv2
        self.save_images = save_images

        self.img_type = cameraTypeMap[img_type]

        if img_benchmark_type == "simGetImage":
            self.image_callback_thread = threading.Thread(target=self.repeat_timer_img, args=(self.image_callback_benchmark_simGetImage, 0.001))
        if img_benchmark_type == "simGetImages":
            self.image_callback_thread = threading.Thread(target=self.repeat_timer_img, args=(self.image_callback_benchmark_simGetImages, 0.001))
        self.is_image_thread_active = False

        if self.save_images:
            self.tmp_dir = os.path.join(tempfile.gettempdir(), "airsim_img_bm")
            print ("Saving images to %s" % self.tmp_dir)
            try:
                os.makedirs(self.tmp_dir)
            except OSError:
                if not os.path.isdir(self.tmp_dir):
                    raise

    def start_img_benchmark_thread(self):
        if not self.is_image_thread_active:
            self.is_image_thread_active = True
            self.benchmark_start_time = time.time()
            self.image_callback_thread.start()
            print("Started img image_callback thread")

    def stop_img_benchmark_thread(self):
        if self.is_image_thread_active:
            self.is_image_thread_active = False
            self.image_callback_thread.join()
            print("Stopped image callback thread.")

    def repeat_timer_img(self, task, period):
        while self.is_image_thread_active:
            task()
            time.sleep(period)

    def print_benchmark_results(self):
        avg_fps = 1.0 / ((self.image_benchmark_total_time) / float(self.image_benchmark_num_images))
        print("result: {} avg_fps for {} num of images".format(avg_fps, self.image_benchmark_num_images))

    def image_callback_benchmark_simGetImage(self):
        self.image_benchmark_num_images += 1
        image = self.airsim_client.simGetImage("front_center", self.img_type)
        np_arr = np.frombuffer(image, dtype=np.uint8)
        img_rgb = np_arr.reshape(240, 512, 4)

        self.image_benchmark_total_time = time.time() - self.benchmark_start_time
        avg_fps = self.image_benchmark_num_images / self.image_benchmark_total_time
        print("result: {} avg_fps for {} num of images".format(avg_fps, self.image_benchmark_num_images))
        # uncomment following lines to viz image
        if self.viz_image_cv2:
            cv2.imshow("img_rgb", img_rgb)
            cv2.waitKey(1)

    def image_callback_benchmark_simGetImages(self):
        self.image_benchmark_num_images += 1
        request = [airsim.ImageRequest("front_center", self.img_type, False, False)]
        response = self.airsim_client.simGetImages(request)

        self.image_benchmark_total_time = time.time() - self.benchmark_start_time
        avg_fps = self.image_benchmark_num_images / self.image_benchmark_total_time
        print("result + {} avg_fps for {} num of images".format(avg_fps, self.image_benchmark_num_images))

        if self.viz_image_cv2:
            np_arr = np.frombuffer(response[0].image_data_uint8, dtype=np.uint8)
            img = np_arr.reshape(response[0].height, response[0].width, -1)
            # print(img.shape)
            cv2.imshow("img", img)
            cv2.waitKey(1)

        if self.save_images:
            filename = os.path.join(self.tmp_dir, str(self.image_benchmark_num_images))
            saveImage(response[0], filename)
            # cv2.imwrite(os.path.normpath(filename + '.png'), img) # write to png


def main(args):
    image_benchmarker = ImageBenchmarker(img_benchmark_type=args.img_benchmark_type, viz_image_cv2=args.viz_image_cv2,
                                      save_images=args.save_images, img_type=args.img_type)

    image_benchmarker.start_img_benchmark_thread()
    time.sleep(30)
    image_benchmarker.stop_img_benchmark_thread()
    image_benchmarker.print_benchmark_results()

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--img_benchmark_type', type=str, choices=["simGetImage", "simGetImages"], default="simGetImages")
    parser.add_argument('--enable_viz_image_cv2', dest='viz_image_cv2', action='store_true', default=False)
    parser.add_argument('--save_images', dest='save_images', action='store_true', default=False)
    parser.add_argument('--img_type', type=str, choices=cameraTypeMap.keys(), default="scene")

    args = parser.parse_args()
    main(args)