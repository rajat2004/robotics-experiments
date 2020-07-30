import airsim
import time

client = airsim.MultirotorClient()
client.confirmConnection()

def setWindAndSleep(wind, sleep_time = 5):
    print("Setting wind to " + str(wind) )
    client.simSetWind(wind)

    time.sleep(sleep_time)


while True:
    # Set wind to (20,0,0) in NED (forward direction)
    wind = airsim.Vector3r(20, 0, 0)
    setWindAndSleep(wind)

    # Set wind to (0,25,0) in NED (towards right)
    wind = airsim.Vector3r(0, 25, 0)
    setWindAndSleep(wind)

    # Set wind to 0
    wind = airsim.Vector3r(0, 0, 0)
    setWindAndSleep(wind)
