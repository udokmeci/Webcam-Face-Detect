import cv2
import os
import sys
import logging as log
import datetime as dt
import syslog
import time
import pygtk

pygtk.require("2.0")
import gtk
import subprocess
import threading
import gobject
from multiprocessing import Process, Queue
from Queue import Empty
import webbrowser



gtk.threads_init()


font = cv2.FONT_HERSHEY_SIMPLEX
cascPath = sys.argv[1]
threshold= int(sys.argv[2]);
showImage= int(sys.argv[3]);


class GtkStatusIcon(object):
    def __init__(self):
        self.data_queue = Queue();
        self.exiting=False;
        self.sleepTime=2;

        self.p = Process(target=self.deamon_start, args=())
        self.p2 = Process(target=self.runGTKApplet, args=())

        self.p.start()
        self.p2.start()

        self.p.join()
        self.p2.join()

    def exit(self):
        self.setStatus("Exit")

    def right_click(self):
        webbrowser.open('file:///last.jpg')
        
    def runGTKApplet(self):
        self.dialog_title = "Test"
        self.STOKICON=gtk.STOCK_YES;
        self.icon= gtk.status_icon_new_from_stock(self.STOKICON)
        gobject.timeout_add(500, self.updateStatus) 
        self.icon.set_tooltip("Test")
        self.icon.connect("popup-menu", self.right_click)
        gtk.main();



    def updateStatus(self):
        # receive updates from the child process here
        try:

            data = self.data_queue.get_nowait()
            if(data=='Exit'):
                gtk.main_quit()
                return True

            print data;
            self.icon.set_from_stock(data);
        except Empty:
            pass
        else:
            self.register_data(data)
        return True


    def register_data(self, data):
        self.STOKICON=data;


    def setStatus(self,data):
        self.data_queue.put(data)

    def setNo(self):
        print('No')
        self.setStatus(gtk.STOCK_NO)

    def setAbout(self):
        print('about')
        self.setStatus(gtk.STOCK_ABOUT)

    def setYes(self):
        print('yes')
        self.setStatus(gtk.STOCK_YES)

    def setDiff(self,diff):
        self.icon.set_tooltip(diff)

    def increaseSleepTime(self):
        print(self.sleepTime)
        if(self.sleepTime<30):
            self.sleepTime=self.sleepTime+1
            return

        self.sleepTime=30

    def deamon_start(self):
        faceCascade = cv2.CascadeClassifier(cascPath)
        sleepTime=1
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
                scaleFactor=1.2,
                minNeighbors=4,
                minSize=(60, 30)
            )

            # Draw a rectangle around the faces
            # 
            
            
            minLevel=10000;
            cv2.line ( gray, (0,threshold),(100,threshold),(0, 255, 0), 2)
            for (x, y, w, h) in faces:
                cv2.rectangle(gray, (x, y), (x+w, y+h), (0, 255, 0), 2)
                if y<minLevel :
                    minLevel=y
                cv2.putText(gray,'%d - %d' % (minLevel , counter) ,(10,minLevel), font, 1,(255,255,255),2)
            if len(faces)>0:
                self.sleepTime = 0.2
                if minLevel>threshold:
                    counter = counter +1
                else:
                    self.setYes()    
                    syslog.syslog(syslog.LOG_INFO, 'Posture OK')
                    counter =0
                    pass
                
                if minLevel>threshold:
                    self.sleepTime = 0.01
                    if counter > 5:
                        self.setNo()
                    else:
                        self.setAbout()   
                    if counter > 10:
                        syslog.syslog(syslog.LOG_ALERT, 'Posture Wrong')
                        os.system('play --no-show-progress --null --channels 1 synth 0.1 sine 2000')
                        cv2.imwrite('/tmp/last.jpg', gray)
                        counter=0
            else:
                self.increaseSleepTime()
                

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


            # Display the resulting frame
            if showImage==1:
                cv2.imshow('Video', gray)


            time.sleep(sleepTime)

        video_capture.release()
        cv2.destroyAllWindows()
        self.exit();

# When everything is done, release the capture

def main():
    GtkStatusIcon()

if __name__ == "__main__":
    main()