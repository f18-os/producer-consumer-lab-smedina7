#!/usr/bin/env python3

import cv2
import time 
import threading
import numpy as np
import base64
import queue
import os

########grayscale
# globals
outputDir    = 'frames'

# initialize frame count
count = 0

# get the next frame file name
inFileName = "{}/frame_{:04d}.jpg".format(outputDir, count)

# load the next file
inputFrame = cv2.imread(inFileName, cv2.IMREAD_COLOR)

while inputFrame is not None:
    print("Converting frame {}".format(count))

    # convert the image to grayscale
    grayscaleFrame = cv2.cvtColor(inputFrame, cv2.COLOR_BGR2GRAY)
    
    # generate output file name
    outFileName = "{}/grayscale_{:04d}.jpg".format(outputDir, count)

    # write output file
    cv2.imwrite(outFileName, grayscaleFrame)

    count += 1

    # generate input file name for the next frame
    inFileName = "{}/frame_{:04d}.jpg".format(outputDir, count)

    # load the next frame
    inputFrame = cv2.imread(inFileName, cv2.IMREAD_COLOR)

##########Display
# globals
outputDir    = 'frames'
frameDelay   = 42       # the answer to everything

# initialize frame count
count = 0

startTime = time.time()

# Generate the filename for the first frame 
frameFileName = "{}/grayscale_{:04d}.jpg".format(outputDir, count)

# load the frame
frame = cv2.imread(frameFileName)

while frame is not None:
    
    print("Displaying frame {}".format(count))
    # Display the frame in a window called "Video"
    cv2.imshow("Video", frame)

    # compute the amount of time that has elapsed
    # while the frame was processed
    elapsedTime = int((time.time() - startTime) * 1000)
    print("Time to process frame {} ms".format(elapsedTime))
    
    # determine the amount of time to wait, also
    # make sure we don't go into negative time
    timeToWait = max(1, frameDelay - elapsedTime)

    # Wait for 42 ms and check if the user wants to quit
    if cv2.waitKey(timeToWait) and 0xFF == ord("q"):
        break    

    # get the start time for processing the next frame
    startTime = time.time()
    
    # get the next frame filename
    count += 1
    frameFileName = "{}/grayscale_{:04d}.jpg".format(outputDir, count)

    # Read the next frame file
    frame = cv2.imread(frameFileName)

# make sure we cleanup the windows, otherwise we might end up with a mess
cv2.destroyAllWindows()


#extractFrames
# globals
outputDir    = 'frames'
clipFileName = 'clip.mp4'
# initialize frame count
count = 0

# open the video clip
vidcap = cv2.VideoCapture(clipFileName)

# create the output directory if it doesn't exist
if not os.path.exists(outputDir):
  print("Output directory {} didn't exist, creating".format(outputDir))
  os.makedirs(outputDir)

# read one frame
success,image = vidcap.read()

print("Reading frame {} {} ".format(count, success))
while success:

  # write the current frame out as a jpeg image
  cv2.imwrite("{}/frame_{:04d}.jpg".format(outputDir, count), image)   
  success,image = vidcap.read()
  print('Reading frame {}'.format(count))
  count += 1



######Extract and Display
def extractFrames(fileName, outputBuffer):
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
        outputBuffer.put(jpgAsText)
       
        success,image = vidcap.read()
        print('Reading frame {} {}'.format(count, success))
        count += 1

    print("Frame extraction complete")


def displayFrames(inputBuffer):
    # initialize frame count
    count = 0

    # go through each frame in the buffer until the buffer is empty
    while not inputBuffer.empty():
        # get the next frame
        frameAsText = inputBuffer.get()

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

# filename of clip to load
filename = 'clip.mp4'

# shared queue  
extractionQueue = queue.Queue()

# extract the frames
extractFrames(filename,extractionQueue)

# display the frames
displayFrames(extractionQueue)
