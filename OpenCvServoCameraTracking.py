import cv2
import numpy as np 
from adafruit_servokit import ServoKit


#---------------------------setup variables
dispW = 500
dispH = 500
flip = 2

pan = 90
tilt = 45
XYservos = ServoKit(channels = 16)
XYservos.servo[0].angle =  pan
moveEnable = 0

camSet='nvarguscamerasrc !  video/x-raw(memory:NVMM), width=3264, height=2464, format=NV12, framerate=21/1 ! nvvidconv flip-method='+str(flip)+' ! video/x-raw, width='+str(dispW)+', height='+str(dispH)+', format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink'
cam =cv2.VideoCapture(camSet)
def nothing(x):
    pass
cv2.namedWindow('Trackbars')
cv2.moveWindow('Trackbars',550,0)
cv2.createTrackbar('hueLower1','Trackbars',0,179,nothing)
cv2.createTrackbar('hueHigher1','Trackbars',0,179,nothing)
cv2.createTrackbar('hueLower2','Trackbars',0,179,nothing)
cv2.createTrackbar('hueHigher2','Trackbars',0,179,nothing)
cv2.createTrackbar('satLower','Trackbars',0,255,nothing)
cv2.createTrackbar('satHigher','Trackbars',0,255,nothing)
cv2.createTrackbar('valLow','Trackbars',0,255,nothing)
cv2.createTrackbar('valHigh','Trackbars',0,255,nothing)

blank = np.zeros([240,360,1],np.uint8)
cv2.createTrackbar('sBlue','Trackbars',0,20,nothing)
cv2.createTrackbar('sGreen','Trackbars',0,20,nothing)
cv2.createTrackbar('sRed','Trackbars',0,20,nothing)
cv2.createTrackbar('thresholdDet','Trackbars',0,30,nothing)

while True:
    ret,frame =cam.read()
    #frame =cv2.imread('smarties.png')

#------------------------Show Frames from PiCam------------------------------------------------------------

    b,g,r =cv2.split(frame)


 
    saturationBlue =cv2.getTrackbarPos('sBlue','Trackbars')
    saturationGreen =cv2.getTrackbarPos('sGreen','Trackbars')
    saturationRed =cv2.getTrackbarPos('sRed','Trackbars')

    b[:]=b[:]*(saturationBlue/10)
    g[:]=g[:]*(saturationGreen/10)
    r[:]=r[:]*(saturationRed/10)

    merge =cv2.merge((b,g,r))
    hsv =cv2.cvtColor(merge,cv2.COLOR_BGR2HSV)

    thresholdDet =cv2.getTrackbarPos('thresholdDet','Trackbars')

    #print(hsv)
    hueLow1 =cv2.getTrackbarPos('hueLower1','Trackbars')
    hueHigh1 =cv2.getTrackbarPos('hueHigher1','Trackbars')

    hueLow2 =cv2.getTrackbarPos('hueLower2','Trackbars')
    hueHigh2 =cv2.getTrackbarPos('hueHigher2','Trackbars')
    #print('hueLow: ',hueLow)
    #print('hueHigh: ',hueHigh)
    Ls =cv2.getTrackbarPos('satLower','Trackbars')
    Hs =cv2.getTrackbarPos('satHigher','Trackbars')
    #print('ls: ',Ls)
    #print('Hs: ',Hs)
    Lv =cv2.getTrackbarPos('valLow','Trackbars')
    Hv =cv2.getTrackbarPos('valHigh','Trackbars')
    #print('Lv: ',Lv)
    #print('Hv: ',Hv)
    l_b1 =np.array([hueLow1,Ls,Lv],np.uint8)
    h_b1 =np.array([hueHigh1,Hs,Hv],np.uint8)

    l_b2 =np.array([hueLow2,Ls,Lv],np.uint8)
    h_b2 =np.array([hueHigh2,Hs,Hv],np.uint8)

    FGmask1 =cv2.inRange(hsv,l_b1,h_b1)
    FGmask2 =cv2.inRange(hsv,l_b2,h_b2)
   # cv2.imshow('FGmask',FGmask1)
   # cv2.moveWindow('FGmask',900,0)
    FGmaskComplete =cv2.add(FGmask1,FGmask2)
    postMask =cv2.bitwise_and(frame,frame,mask=FGmaskComplete)
    
    #cv2.imshow('postMask',postMask)
    #cv2.moveWindow('postMask',0,600)

    BGmaskComplete =cv2.bitwise_not(FGmaskComplete)
    BGComplete =cv2.cvtColor(BGmaskComplete,cv2.COLOR_GRAY2BGR)
    
    contours, hierarchy =cv2.findContours(FGmaskComplete,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    contours =sorted(contours,key=lambda x:cv2.contourArea(x),reverse =True)
    
    for cnt in contours:
        area =cv2.contourArea(cnt)
        (x,y,w,h) = cv2.boundingRect(cnt)
        if area>=200:
            cv2.rectangle(merge,(x,y),(x+w,y+h),(255,0,0),3)
    #--------------draw line--------------------------
            objX = int(x+(w/2))
            objY = int(y+(h/2))
            errorPan = objX -  250
            errorTilt = objY - 250
            cv2.line(merge,(objX,0),(objX,500),(0,255,0),4)  
            #cv2.drawContours(frame,[cnt],0,(0,255,0),3)
            cv2.line(merge,(0,objY),(500,objY),(0,255,0),4) 
            if moveEnable == 1:
                if abs(errorPan)>30:
                    pan = pan - errorPan/thresholdDet
                if abs(errorTilt)>30:
                    tilt = tilt - errorTilt/thresholdDet
                if pan > 180:
                    pan = 180
                    print ('Pan Out of Range')
                if pan < 0:
                    pan = 0
                    print ('Pan Out of Range')
                if tilt > 180:
                    tilt = 180
                    print ('Tilt Out of Range')
                if tilt < 0:
                    tilt = 0
                    print ('Tilt Out of Range') 
                XYservos.servo[0].angle = pan
                #XYservo[1].angle = tilt
            break                 
#----- show results in final windows
    cv2.imshow('piCam',merge)
    cv2.moveWindow('piCam',0,0)
    finalWindow =cv2.add(postMask,BGComplete)
    cv2.imshow('FinalWindow',finalWindow)
    cv2.moveWindow('FinalWindow',900,0)


    if cv2.waitKey(1)==ord('q'):
        break
    if cv2.waitKey(1)==ord('e'):
        moveEnable = 1
        print ('Enable')
        
    if cv2.waitKey(1)==ord('d'):
        moveEnable = 0
        print ('Disenable')

cam.release()
cv2.destroyAllWindows()