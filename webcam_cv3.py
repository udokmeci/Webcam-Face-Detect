import cv2
import os
import sys
import logging as log
import datetime as dt
import syslog
import time
font = cv2.FONT_HERSHEY_SIMPLEX
cascPath = sys.argv[1]
threshold= int(sys.argv[2]);
showImage= int(sys.argv[3]);
faceCascade = cv2.CascadeClassifier(cascPath)

video_capture = cv2.VideoCapture(0)


counter = 0;
while True:
    if not video_capture.isOpened():
        syslog.syslog(syslog.LOG_ERR, 'Unable to load camera.')
        sleep(5)
        pass

    # Capture frame-by-frame
    ret, frame = video_capture.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=7,
        minSize=(10, 10)
    )

    # Draw a rectangle around the faces
    # 
    
    
    minLevel=10000;
    cv2.line ( frame, (0,threshold),(100,threshold),(0, 255, 0), 2)
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        if y<minLevel :
            minLevel=y
        cv2.putText(frame,'%d - %d' % (minLevel , counter) ,(10,minLevel), font, 1,(255,255,255),2)
    if len(faces)>0:
        if minLevel>threshold:
            counter = counter +1
        else:
            if counter>5:
                syslog.syslog(syslog.LOG_INFO, 'Posture OK')
                #os.system('play --no-show-progress --null --channels 1 synth 0.05 sine 400')
            
            counter =0
            pass
        
        if minLevel>threshold and counter > 20:
            syslog.syslog(syslog.LOG_ALERT, 'Posture Wrong')
            os.system('play --no-show-progress --null --channels 1 synth 0.1 sine 2000')
            counter=0

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


    # Display the resulting frame
    if showImage==1:
        cv2.imshow('Video', frame)


    time.sleep(0.2)

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()
