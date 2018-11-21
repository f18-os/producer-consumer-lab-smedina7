#!/usr/bin/env python3

from threading import Thread
import threading
import cv2
import numpy as np
import base64
import queue

# filename of clip to load
filename = 'clip.mp4'

# shared queue  
extractionQueue = queue.Queue(10)

# output queue
outQueue = queue.Queue(10)

#semaphores
sem_putExt = threading.Semaphore(10)
sem_putOut = threading.Semaphore(10)
sem_getExt = threading.Semaphore(0)
sem_getOut = threading.Semaphore(0)


def extractFrames(fileName):
    # Initialize frame count 
    count = 0

    # open video file
    vidcap = cv2.VideoCapture(fileName)

    # read first image
    success,image = vidcap.read()
    
    print("Reading frame {} {} ".format(count, success))
    while success:
        # get a jpg encoded frame
        success, jpgImage = cv2.imencode('.jpg', image)

        #encode the frame as base 64 to make debugging easier
        jpgAsText = base64.b64encode(jpgImage)

        # add the frame to the buffer
        sem_putExt.acquire()
        extractionQueue.put(jpgAsText)
        sem_getExt.release()
       
        success,image = vidcap.read()
        print('Reading frame {} {}'.format(count, success))
        count += 1

    print("Frame extraction complete")
    
    sem_putExt.acquire()
    extractionQueue.put("Frame extraction complete")
    sem_getExt.release()


def displayFrames():
    # initialize frame count
    count = 0

    # go through each frame in the buffer until the buffer is empty
    while(1):
        
        # get the next frame
        sem_getOut.acquire()
        frameAsText = outQueue.get()
        
        if(frameAsText == "Break"):
           print("Done")
           break
        
        sem_putOut.release()
        
        

        # decode the frame 
        jpgRawImage = base64.b64decode(frameAsText)

        # convert the raw frame to a numpy array
        jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)
        
        # get a jpg encoded frame
        img = cv2.imdecode( jpgImage ,cv2.IMREAD_UNCHANGED)

        print("Displaying frame {}".format(count))        

        # display the image in a window called "video" and wait 42ms
        # before displaying the next frame
        cv2.imshow("Video", img)
        if cv2.waitKey(42) and 0xFF == ord("q"):
            break

        count += 1

    print("Finished displaying all frames")
    # cleanup the windows
    cv2.destroyAllWindows()

def convertToGreyscale():
    
    while(1):
        sem_getExt.acquire()
        frameAsText = extractionQueue.get()
        
        if(frameAsText == "Frame extraction complete"):
            #sem_putOut.acquire()
            outQueue.put("Break")
            print("Grey Done")
            sem_getOut.release()
            break
        
        sem_putExt.release()
        
       
        #from EXTRACT AND DISPLAY
        
        #decode the frame
        jpgRawImage = base64.b64decode(frameAsText)
    
        # convert the raw frame to a numpy array
        jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)
    
        # get a jpg encoded frame
        img = cv2.imdecode( jpgImage ,cv2.IMREAD_UNCHANGED)
        
        #from convertToGreyscale
        
        # convert the image to grayscale
        grayscaleFrame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # get a jpg encoded frame
        success, jpgImage = cv2.imencode('.jpg', grayscaleFrame)
        
        #from extract frames def
        
        #encode the frame as base 64 to make debugging easier
        jpgAsText = base64.b64encode(jpgImage)
        
        #put to gray 
        sem_putOut.acquire()
        outQueue.put(jpgAsText)
        sem_getOut.release()

thread1 = Thread(target = extractFrames, args=[filename])
thread2 = Thread(target = convertToGreyscale, args=[])
thread3 = Thread(target = displayFrames, args=[])

thread1.start()
thread2.start()
thread3.start()

# extract the frames
#extractFrames(filename)

#convert to conver to Greyscale
#convertToGreyscale()

# display the frames
#displayFrames()
