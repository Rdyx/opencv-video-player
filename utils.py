from tkinter import Tk


# Getting screen resolution to calculate windows' size
def getScreenSize():
    root = Tk()
    screenWidth = root.winfo_screenwidth()
    screenHeight = root.winfo_screenheight()
    root.withdraw()

    return {'screenWidth': screenWidth, 'screenHeight': screenHeight}


# Setting windows parameters
def setWindow(cv2, windowName, windowWitdh, windowHeight, windowPositionX, windowPositionY):
    cv2.namedWindow(windowName, cv2.WINDOW_GUI_NORMAL)
    cv2.resizeWindow(windowName, windowWitdh, windowHeight)
    cv2.moveWindow(windowName, windowPositionX, windowPositionY)


# Setting waitKey is influing on video read speed so we calculate the refresh based on the fps
# Due to processing we make it slighty faster (-5)
# I.e: 30 fps video is resulting in 33fps means waitKey will be 28ms
def setCv2Key(cv2, frameRate):
    frameRate = (int((1/frameRate)*1000)-5) if frameRate != 0 else 0
    frameRate = frameRate if frameRate > 10 else 10 if frameRate != 0 else 0
    return cv2.waitKey(frameRate) & 0xFF


# Converting frame number in time
def setFrameToMsec(frameNumber, frameRate):
    duration = frameNumber/frameRate
    minutes = int(duration/60)
    seconds = int(duration % 60)
    seconds = ('0' + str(seconds)) if seconds < 10 else seconds

    # return float(str(minutes) + '.' + str(seconds))
    return '{}:{}'.format(minutes, seconds)


# Convertime time in frame number
def setMsecToFrameNumber(duration, frameRate):
    duration = duration.split(':')
    # Get secs from minutes
    minutes = float(duration[0])*60
    seconds = float('0' + duration[1] if duration[1] < 10 else duration[1])

    return int((minutes*frameRate) + (seconds*frameRate))


# Update video time (human readable stuff)
def updateVideoTime(cap, cv2, frameNumber, frameRate, totalFrames, Controls):
    cv2.rectangle(Controls, (0, 0), (100, 100), 0, -1)
    time = setFrameToMsec(frameNumber, frameRate)

    return cv2.putText(
        Controls,
        '{} / {}'.format(
            str(time),
            setFrameToMsec(totalFrames, frameRate)
        ),
        (20, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.4,
        255
    )
