import numpy as np
import cv2
import time
import utils as u
import sys
import os

from tkinter import Tk

# Checking if we can open the linked file
if len(sys.argv) > 1:
    videoInput = sys.argv[1]
else:
    videoInput = input('Please enter video path: ')

try:
    if 'http' in videoInput:
        videoPath = videoInput
    else:
        if open(videoInput):
            videoPath = videoInput
except IOError:
    raise IOError(
        'Please enter a valid path. Use "" if you have spaces in the path.')

cap = cv2.VideoCapture(videoPath)


######### CONFIGURATION #########
######### PLAYER #########
# Get screen width
screenWidth = u.getScreenSize()['screenWidth']
# Get screen height
screenHeight = u.getScreenSize()['screenHeight']
# Get video frame rate
frameRate = cap.get(cv2.CAP_PROP_FPS)
# Used for video duration calculation
baseFrameRate = frameRate
# Init buffer array
frameList = []
# Modify this number to increase or decrease buffer size (+1 is about array indexes)
maxFrames = 90 + 1
# Total frames in the video
totalFrames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
# Seconds to ignore when clicking on bar, too low value would make the player slow
secondsToIgnore = 3
# Start time (s)
startTime = 0
# Create Controls window content
Controls = np.zeros((50, 750), np.uint8)
# Set Controls window text
controlString = "Space: Play/Pause, A: Previous Frame, E: Next Frame, Esc: Close Player"
cv2.putText(
    Controls, controlString, (120, 30),
    cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255
)
# Separator line for time and controls (Aesthetic)
cv2.line(Controls, (108, 0), (108, 500), (255, 255, 255))

videoWindowName = 'Video'
controlsWindowName = 'Controls'
frameNumberTrackbarName = 'Frame Number'
framerateTrackbarName = 'Frame Rate'
######### !PLAYER #########

######### COMMANDS #########
playCommand = 'play'
pauseCommand = 'pause'
prevFrameCommand = 'prev_frame'
nextFrameCommand = 'next_frame'
replayCommand = 'replay'
exitCommand = 'exit'

# Set default status at player opening
status = playCommand

# Status dict, modify letters to update shortcuts
videoStatus = {
    # Uncomment if you want a play button, but should not be necessary since
    # We trigger play/pause from pause
    # ord('w'): playCommand, ord('W'): playCommand,

    32: pauseCommand,           # Space
    ord('a'): prevFrameCommand,
    ord('e'): nextFrameCommand,
    ord('r'): replayCommand,
    -1: status,                 # If no key is pressed, get the previous status
    27: exitCommand             # Esc
}
######### !COMMANDS #########
######### !CONFIGURATION #########


# Start time (ms)
cap.set(cv2.CAP_PROP_POS_MSEC, startTime*1000)

# Create Controls window
u.setWindow(
    cv2, controlsWindowName,
    int(screenWidth*0.8), int(screenHeight*0.2),
    int(screenWidth*0.1), int(screenHeight*0.72)
)

# Create Video window
u.setWindow(
    cv2, videoWindowName,
    int(screenWidth*0.8), int(screenHeight*0.6),
    int(screenWidth*0.1), int(screenHeight*0.08)
)


# Time jump must be more than X seconds to be taken in account (X = framerate*seconds)
def modifyFrameNumber(newFrameNumber, currentFrameNumber, frameRate=frameRate, secondsToIgnore=secondsToIgnore, cap=cap):
    global frameList

    supposedPreviousFrameNumber = int(frameNumber-(frameRate*secondsToIgnore))
    supposedNextFrameNumber = int(frameNumber+(frameRate*secondsToIgnore))

    # Ignore click if replay mode
    if status == replayCommand:
        pass
    # Ignore click if it's too close form current time and reset buffer if it's success
    elif newFrameNumber not in range(supposedPreviousFrameNumber, supposedNextFrameNumber):
        frameList = []
        cap.set(
            cv2.CAP_PROP_POS_FRAMES,
            cv2.getTrackbarPos(frameNumberTrackbarName, controlsWindowName)
        )
    # If we use prev or next frame, standard process
    elif status in [prevFrameCommand, nextFrameCommand]:
        cap.set(cv2.CAP_PROP_POS_FRAMES, newFrameNumber)


def modifyFrameRate(newFrameRate):
    global frameRate
    global status

    isNewFrameRateZero = newFrameRate == 0
    # If framerate is manually set to 0, it means pause
    # We set status because frameRate to 0 would make cv2.keyWait() crash
    # Watch out, we have to press pause key to resume playing
    if isNewFrameRateZero:
        status = pauseCommand
    else:
        frameRate = newFrameRate


# Simple method to update trackbar (and video frame) if we use prev_frame or next_frame
def changeCurrentFrame(frameNumber, step, trackbarName=frameNumberTrackbarName, windowName=controlsWindowName, cv2=cv2):
    newValue = cv2.getTrackbarPos(trackbarName, windowName) + step
    cv2.setTrackbarPos(trackbarName, windowName, newValue)


# Create trackbars method
def setTrackBar(trackbarName, windowName, defaultButtonPosition, end, func, cv2=cv2):
    return cv2.createTrackbar(
        trackbarName, windowName, defaultButtonPosition,
        end, func
    )


# Create Frame Number trackbar (this one uses modifyFrameNumber method)
setTrackBar(
    frameNumberTrackbarName, controlsWindowName, 0, totalFrames,
    lambda value: modifyFrameNumber(
        value, cv2.getTrackbarPos(frameNumberTrackbarName, controlsWindowName))
)

# Create Frame Rate trackbar (this one uses modifyFrameRate method)
setTrackBar(
    framerateTrackbarName, controlsWindowName, int(frameRate),
    int(frameRate), modifyFrameRate
)

# Infinite loop, we break it manually every time
# Used to be able to process differently after each frame depending on status
while(True):
    # Update video time
    cv2.imshow(controlsWindowName, Controls)
    # Get the framenumber before we process anything
    frameNumber = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
    # Set current status to know in which condition we will get
    status = videoStatus.get(u.setCv2Key(cv2, frameRate), status)

    # Read video frames
    ret, frame = cap.read()
    cv2.imshow(videoWindowName, frame)

    # Update Frame Number trackbar and video time
    cv2.setTrackbarPos(
        frameNumberTrackbarName,
        controlsWindowName,
        frameNumber
    )
    u.updateVideoTime(
        cap, cv2, frameNumber,
        baseFrameRate, totalFrames, Controls
    )

    # When pause is started, we listen to 4 commands
    # For any other key we keep in pause
    while status == pauseCommand:
        status = videoStatus.get(u.setCv2Key(cv2, 0), None)
        if status == pauseCommand:
            status = playCommand
            # In case of pause from framerate set to 0, pressing pause button will unpause
            # And set the frame rate trackbar button position to its last value
            cv2.setTrackbarPos(
                framerateTrackbarName, controlsWindowName, int(frameRate))
        elif status in [prevFrameCommand, nextFrameCommand, replayCommand, exitCommand]:
            pass
        else:
            status = pauseCommand

    # Condition to get back/forward frame by frame
    if status in [prevFrameCommand, nextFrameCommand]:
        if status == prevFrameCommand:
            changeCurrentFrame(frameNumber-1, -1)
        elif status == nextFrameCommand:
            changeCurrentFrame(frameNumber+1, 1)

        status = pauseCommand
        continue

    # Replay last X secs with backward/forward style
    if status == replayCommand:
        backwardPlay = True
        # Starting from last buffered frame to go backward
        index = len(frameList)
        # Listening to keys into replay so we are able to pause
        # And use frame by frame keys, default to None at start
        # Then getting reset once we get in the next while loop
        newStatus = videoStatus.get(u.setCv2Key(cv2, frameRate), None)

        # Untill we press replay key again, we will loop backward/forward
        while status == replayCommand:
            if backwardPlay:
                index -= 1
                if index == 0:
                    backwardPlay = False
            else:
                index += 1
                if index == len(frameList) - 1:
                    backwardPlay = True

            # In case of pause from framerate, standard method is not enough
            # Since it's replacing the global status. We have to reset it manually after check
            # And tell this loop to pause if framerate is set to 0
            frameRateTrackbarPos = cv2.getTrackbarPos(
                framerateTrackbarName, controlsWindowName)
            if frameRateTrackbarPos == 0:
                newStatus = pauseCommand
                status = replayCommand

            # Using same principle as first big while loop, we listen to keys to know
            # How to process actions in the replay
            newStatus = videoStatus.get(u.setCv2Key(cv2, frameRate), newStatus)

            # Exiting will break loop and kill player
            if newStatus == exitCommand:
                status = newStatus
                break
            # Pressing replay key again will break the replay loop
            elif newStatus == replayCommand:
                status = playCommand
                break
            # Pause in replay
            elif newStatus == pauseCommand:
                while newStatus == pauseCommand:
                    newStatus = videoStatus.get(u.setCv2Key(cv2, 0), None)
                    if newStatus == pauseCommand:
                        # Just to get out of pause loop
                        newStatus = 'keepPlayReplay'
                        # In case of pause from framerate set to 0, reset the trackbar button pos
                        cv2.setTrackbarPos(
                            framerateTrackbarName,
                            controlsWindowName,
                            int(frameRate)
                        )
                        continue
                    else:
                        break

            # Using prev_fram and next_frame keys in replay
            if newStatus in [prevFrameCommand, nextFrameCommand]:
                if newStatus == prevFrameCommand:
                    # If we're going forward, index will +1 at start of loop
                    # So we have to -2 to get the previous frame
                    # If index is getting under 0, force it to 0
                    if not backwardPlay:
                        if index-2 > 1:
                            index -= 2
                        else:
                            index = 0
                elif newStatus == nextFrameCommand:
                    # If we're going backward, index will -1 at start of loop
                    # So we have to +2 to get the previous frame
                    # If index is getting under 0, force it to "array length -1" (last valid index)
                    if backwardPlay:
                        if ((index+3) <= len(frameList)):
                            index += 2
                        else:
                            index = len(frameList)-1
                # Pause after key
                newStatus = pauseCommand

            # Get the replay frame number to be able to update Frame Number trackbar
            frameNumber = frameList[index][1]
            # Get the frame
            rframe = frameList[index][0]
            # Update video time
            u.updateVideoTime(
                cap, cv2, frameNumber,
                baseFrameRate, totalFrames, Controls
            )

            # Show frame in player and update the rest accordingly
            cv2.imshow(videoWindowName, rframe)
            cv2.setTrackbarPos(
                frameNumberTrackbarName,
                controlsWindowName,
                frameNumber
            )
            cv2.imshow(controlsWindowName, Controls)

    # Is escape is pressed, exit video
    if status == exitCommand:
        break

    # If we reach end of video, close it by breaking loop
    if frameNumber == totalFrames and status == playCommand:
        break

    # Used to adapt video speed to frame rate trackbar value
    if status == playCommand:
        time.sleep((0.1-frameRate/1000.0)**21021)

    # If image has been processed normally, store it in buffer
    # "Buffering" for backward play
    # Simply store the frame in an array
    frameList.append((frame, frameNumber))

    # Creating sliding window system by cleaning the first index and append a new one
    if len(frameList) > maxFrames:
        del frameList[0]
    if frameList[::-1] == None:
        frameList.pop()


# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
