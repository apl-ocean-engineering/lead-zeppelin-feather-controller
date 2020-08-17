# Lead Zeppelin Seaglider Controller Project

## Introduction
The Lead Zeppelin is an ongoing student project to develop a small, low cost buoyancy-driven glider.  An ME capstone group just completed a redesign of the buoyancy and pitch control systems for the glider, with a plan to build and test a prototype within the semester. Due to the COVID-19 quarantine, this prototype was not completed, however we are now planning to build major components of the prototype over the summer.

The existing Lead Zeppelin is controlled by a Raspberry Pi 3 with a motor control Hat. 

The goal of this project is to develop a simple seaglider control system using a simpler microcontroller.

## Hardware
The Lead Zeppelin uses the following Adafruit Feather boards:

- [Adafruit nRF52840 Sense](https://www.adafruit.com/product/4516)
- [Adafruit Adalogger FeatherWing](https://www.adafruit.com/product/2922)
- [Adafruit LoRa Radio FeatherWing - RFM95W 433 MHz](https://www.adafruit.com/product/3232)
- [Adafruit Ultimate GPS FeatherWing](https://www.adafruit.com/product/3133)
- [Adafruit Stepper + DC Motor FeatherWing](https://www.adafruit.com/product/2927) **(Untested)**

For testing, these boards are currently joined with an [Adafruit Quad Side-By-Side](https://www.adafruit.com/product/4254) kit.

In addition, it uses the following Blue Robotics sensors:

- [Bar30 High-Resolution 300m Depth/Pressure Sensor](https://bluerobotics.com/store/sensors-sonars-cameras/sensors/bar30-sensor-r1/)
- [Celsius Fast-Response, ±0.1°C Temperature Sensor](https://bluerobotics.com/store/sensors-sonars-cameras/sensors/celsius-sensor-r1/) **(Untested)**

These sensors are connected to the Feather boards with a custom soldered [FeatherWing Proto](https://www.adafruit.com/product/2884).

Separately, there is a receiving radio station with the following Adafruit Feather boards:
- [Adafruit Feather M0 Adalogger](https://www.adafruit.com/product/2796)
- [Adafruit LoRa Radio FeatherWing - RFM95W 433 MHz](https://www.adafruit.com/product/3232)

Out of these boards and sensors, the Adafruit Stepper + DC Motor FeatherWing and the Celsius Fast-Response, ±0.1°C Temperature Sensor are currently untested. The motor add-on was not tested because there were no servos or motors to test it with during the initial development of the code. The temperature sensor was not tested because there is an i2c address conflict between it and the nRF52840 Sense sensors. In particular, both the sensor and the temperature sensor integrated in the Sense use the 0x77 address, and it does not seem possible to change the address or use a different protocol for either.

## Software
The script for the stack and the sensor is written in CircuitPython and is designed to be as modular as possible. (As a quick note, the Adafruit Feather M0 has limited storage, so it only has the relevant subset of files stored on it.)

### Main Structure
At a high level, the script runs startup code, then enters the main loop. The main loop runs code every loop (i.e. as fast as possible) and every tick (where the duration of a tick is defined in the settings). Details can be found in **code.py**.

### Devices
The functions for each physical board are stored in individual files. Within each file, there are one or more classes that inherit a generic **Wing** class. Boards that combine two or more separate features (such as the Adalogger, which has a real-time clock and SD card storage) will have a class for each feature. All device files are stored in the "devices" folder.

Each Wing subclass can optionally specify code to be run every loop iteration and/or every tick (e.g. refreshing the sensors each tick).

### Modes and Tasks
The script is always in one of many user-defined modes. Within each mode, the script runs a different list of tasks. These tasks are instances of custom classes that inherit a generic **Task** class. All custom modes, tasks, and additional script settings are stored in a single separate file (indicated by redirect.py) that can be swapped out for different configurations.

For the most part, the tasks work independently. However, they can access all devices and tasks, meaning that tasks can be used to add, modify, or delete other tasks. In particular, this is used to allow real-time changes to the program via Bluetooth.

Each Task subclass can optionally specify code to be run every loop iteration and/or every tick (e.g. logging data every tick). 

A sample configuration may have the following files:
- code.py, which contains the main loop.
- redirect.py, which redirects code.py to the file with all tasks and settings (in this example, stack_command.py).
- stack_command.py, which contains all tasks and program settings.
- adalogger.py, bar30.py, ms5837.py, nRF52840.py, rfm9x.py, ultimate.py, and wing.py in the devices folder, which contain device functions.

Note that code.py is generic and can be used for all configurations. If needed, it would be possible to have multiple versions of the task/setting file and switch between them quickly by changing redirect.py.

A sample configuration may have the following modes and respective tasks (the sensors update by default, so that is not included here):
- Update mode - Bluetooth task configuration and high rate data transfer, ascent to surface.
- Idle mode - low rate radio transmission, low rate data logging, ascent to surface.
- Mission mode - low rate radio transmission, data logging, steering, and ascent/descent.

## Issues, Notes, and Future Improvements
Issues:
- The motors remain untested.
- The Blue Robotics temperature sensor is unusable due to the i2c address conflict. The depth sensor can detect temperature, but to a lesser degree.
- Further error detection and handling is necessary to ensure basic function in case the software fails, which would cause the program to stop permanently. If this occurs in operation, the glider may become unrecoverable.
- The code for the Bar30 pressure sensor was adapted from two sources because there was no CircuitPython library available. While it should be good in theory, practical tests are probably necessary to guarantee it is correct.

Notes:
- All devices must be functioning and give a positive test before the program begins the main loop.
- The radio is one way because it is best effort and sending/receiving will block the code from doing anything else. A primative handshake is available to ensure connection between the stack and station, but nothing more.
- The station operates on old code. While it works fine for receiving, it may need to be updated later.
- Bluetooth communications are currently conducted with the Adafruit Bluefruit Connect app.
- The radio and GPS may possibly interfere with each other if they are placed closely.
- If the program terminates at the wrong time while writing, it may cause the SD card to become undetectable. Unplugging the boards and formatting the card seems to fix, but not solve, this problem.
- The task model probably violates theory and best practices in various places (sorry).

Future Improvements:
- Currently it's not possible to modify the behavior of tasks via Bluetooth, though this should be a simple fix.
- Bluetooth only accepts 20 characters at a command. This problem was temporarily sidestepped by reducing the length of the command names.
- Secure communcation for Bluetooth may be necessary in a practical setting.
- Bluetooth file transfer is theoretically possible but not currently available.
- Further modularization for the modes would enable the program to run on one mode while files for other modes are swapped out.

## Development and Maintenance
This software was developed by Axel Li (github:inferee) and last updated 8/17/2020; however future development and maintenance will likely be conducted by other individual(s).