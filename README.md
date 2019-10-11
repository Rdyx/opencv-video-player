# opencv-video-player

This script is using OpenCV in python for **backward/forward** video feature.

If you wish to modify something in the player (i.e buffer time), please edit the setted variables in **CONFIGURATION**.

## Summary
1. Installation
    1. Requirements
    2. Command lines
        1. Install Dependencies
        2. Start player
        3. Create an exportable exec file
2. How to use
3. Known Bugs

## 1. Installation
1. Requirements
    - [Python 3.7.3+](https://www.python.org/downloads/release/python-373/)
    - [virtualenv/venv](https://virtualenv.pypa.io/en/latest/) (Python best practices)

2. Command lines
    1. Install Dependencies
        ```shell
        # Create your virtual environment
        virtualenv -p python3 venv

        # Activate it
        . venv/bin/activate

        # Install dependencies
        pip install -r reqs.txt
        ```

    2. Start player
        ```shell
        # You can directly set a start at a given time (seconds only)
        python openCV-player.py "{VIDEO PATH}" {WANTED START FRAME}
        ```

    3. Create an exportable exec file
        You can create an exportable file to use the script without the need of installing the dependencies by using [pyinstaller](https://pyinstaller.readthedocs.io/en/stable/installation.html):
        ```shell
        # --path is used to get your virtualenv librairies
        pyinstaller --onefile --paths ./venv/lib/python3.7/site-packages/ openCV-player.py
        ```

## 2. How to use
If you followed the installation instructions, you should now have an "opencv player" opened.

You should have **two** windows: "Video" and "Controls".

Frames from video will be displayed in **Video** and you can control the player with **Controls**.

You'll find a brief note with binds in **Controls**:
   - Press **Space** to **Play/Pause** video
   - Press **A** to go to the **previous frame**
   - Press **E** to go to the **next frame**
   - Press **Esc** to **close** the player

You can also click directly on the **Frame Number** bar to go to a desired moment of the video and on the **Frame Rate** trackbar to modify the speed of the video.

*Setting **Frame Rate** to 0 will **pause** the video. You'll have to press **Space** to resume the player.* 

> To avoid unnecessary and heavy useless process, the minimum click distance should be at least **FPS*N second**, where FPS is the video framerate (retrieved by opencv directly). *Defaults to 3 seconds steps*.

> Please note that the **Frame Number** trackbar click is disabled in **backward/forward** mode to avoid unexpected crashes.

## 3. Known Bugs
   - From some tests, it seems that **Frame Number** trackbar value is sometimes incorrect when you start a **backward/forward** after having used multiple times previous/next frame feature. This should not impact your usage in any way, it's more an aesthetic thing than anything else.