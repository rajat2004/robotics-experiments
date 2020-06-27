import airsim
import time

cl = airsim.CarClient()
cl.confirmConnection()

count = 0

for i in range(1000):
    lidarData = cl.getLidarData()
    lidarSegData = cl.simGetLidarSegmentation()

    print(f"Lidar: {len(lidarData.point_cloud)}")
    # time.sleep(0.1)
    print(f"LidarSeg: {len(lidarSegData)}")
    if(len(lidarSegData) != len(lidarData.point_cloud)//3):
        print("Not equal")
        count+=1

    time.sleep(0.1)

print(count)
