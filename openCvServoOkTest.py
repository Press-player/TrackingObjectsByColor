from adafruit_servokit import ServoKit
import time 

mykit = ServoKit(channels = 16)
while True:
    for i in range(180,0,-1):
        mykit.servo[0].angle = i
        time.sleep(.002)    
    time.sleep(.1) 
    for i in range(0,180,1):
        mykit.servo[0].angle = i
        time.sleep(.002)                 


