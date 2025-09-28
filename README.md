# untitled-flash-card-project
An electronic flash card device to aid learning

## Setup
I'm using Waveshare ePaper for this project - you'll need the drivers from their repo

[https://github.com/waveshareteam/Pico_ePaper_Code](Pico ePaper Code Repository)

Once you've cloned it, you'll need the following folders/files copied from the "pythonNanoGui" folder, into a "lib" folder in this repository's Application directory:

* drivers
* gui
* color_setup.py

Follow the instructions [https://raw.githubusercontent.com/waveshareteam/Pico_ePaper_Code/refs/heads/main/pythonNanoGui/ReadMe_EN.txt](here) to ensure the correct drivers are used in the waveshare setup.

Download and copy the [https://raw.githubusercontent.com/RaspberryPiFoundation/picozero/refs/heads/main/picozero/picozero.py](picozero.py) file and copy it to the "lib" folder.