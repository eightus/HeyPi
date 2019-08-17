# Tutorial Documentation of Heypi 

## Table of Contents

1. Introduction
2. Hardware Requirements
3. Setting up the Raspberry Pi
4. Installation of Required Modules
5. Running the Software
6. Voice Commands
7. Web Interface
8. Architecture
9. How HeyPi Works
10. Basic Requirement Evidence
11. Bonus Feature
12. Quick-Start Guide



### 1. Introduction

Heypi is a project done as an experiment which has a voice chat system that utilizes cloud services to carry out its functions. With the implementation of IOT products such as DHT and light sensors Heypi is able to offer more than just a typical voice chat application. Real time reports of the temperature and light can be seen, in future implementation of heypi we can make both end users of the application understand the other client's environment more. 

A Youtube link of our project can be found at 

```
<a href="" target="_blank"><img src="http://img.youtube.com/vi/YOUTUBE_VIDEO_ID_HERE/0.jpg" 
alt="IMAGE ALT TEXT HERE" width="240" height="180" border="10" /></a>
```

### 2. Hardware Requirements

Do ensure the following sensors, resistors and amount of cables are present before setting up

- 1 x DHT 11 Sensor
- 1 x LED 
- 1 x  MCP3008 ADC
- 1 x  Light sensitive resistor
- 1 x button
- 2 x Resistor  10k ohms
- 2 x Resistor 330 ohms 
- 22 x wires 

### 3. Setting up the Raspberry Pi

Setting up of the Raspberry pi is rather straight forward. The end result will look something like this

![Finished](./Images/finished.jpg?raw=true)

A fritzing.jpg attached on this github. The exact replication will be required to be setup in order for the application to work without any issues.

![Fritzing diagram](./Images/Fritzing.png?raw=true)

### 4. Installation of required Modules

```bash
sudo apt-get install 
```

- Modules:

  - ```
    adafruit_dht
    espeak
    mosquitto
    mosquitto-clients
    python3
    python3-dev
    python3-pip
    python3-pyaudio
    flac
    ```

After python3-pip is installed, we will be able to use `sudo pip3 install` command.

```bash
sudo pip3 install
```

- Modules:

  - ```
    adafruit_dht
    contextlib2
    cryptography
    espeak
    flaky
    flask
    gcp-devrel-py-tools
    google-auth
    google-auth-httplib2
    google-cloud-pubsub
    google-cloud-storage
    google-cloud-tools
    gpiozero
    mysql-connector-python
    oauth2
    oauth2client
    picamera
    pyjwt
    wave
    ```

HeyPi is coded in Python3 instead of Python2 due to Python2 is going to be depreciated in 2020

### 5. Running the Software

1. Run the pi.py application with the following arguments **e.g (`sudo python3 pi.py -u user - p password123`)** The application will automatically generate an RSA key, create a device on the IoT Core on google, and establish as well as create an account on our web 

   ***Do note the password and username entered will be used on the web interface later.**

2. Log onto the web interface at http://heypi-iot.appspot.com/login

3. Voice Record function
   - Press and Hold button
   - Speak into mic
   - Release the button

4. Once the voice message is recorded the program will upload it into the cloud storage and all other pi subscribed to the MQTT topic will receive and download the voice file from the cloud storage

5. Dashboard will update itself periodically based on the MQTT transmissions from the pi. 

6. An LED can be turned on and off on the dashboard by clicking and/or speaking into the microphone.

### 6. Voice Command mode

By default, when a new user is created, a few voice command will be added.

##### Default Voice Command

- If `temperature` contains in the audio, Rasperry Pi will reply the current temperature
- If `humidity` contains in the audio, Raspberry Pi will reply the current humidity
- If `brightness` contains in the audio, Raspberry Pi will reply the current brightness
- If `LED` contains in the audio, Raspberry Pi will toggle the LED status
- If `broadcast` contains in the audio, Raspberry Pi will send the audio to all other devices
- If `voicemail` contains in the audio, Raspberry Pi will play all audio that are received from other devices.

Voice command conditions can be configured and added through the web interface. It is highly customizable which allow users to choose and type any voices condition they like. Users can also make the Raspberry Pi reply custom replies base on their liking.



### 7. Web Interface

The login page of heypi:

![Fritzing diagram](./Images/login.png?raw=true)

Dashboard:

![Fritzing diagram](./Images/dashboard.png?raw=true)

Realtime Graphs:

![Fritzing diagram](./Images/realtime.png?raw=true)

### 8. Architecture

< i later do >

### 9. How HeyPi Works

1. When the button is pressed, HeyPi will spawn a thread to start a recording of audio with the help of the PyAudio libary (a library that allows recording with python)
2. Once the button is released, HeyPi will output the audio to a file called output.wav
3. The program will then process the audio file and interpret the speech from the user
4. Once the speech is confirmed, it will move on to compare the speech with conditions that was specified by the user
5. Lastly, once the condition is met, an action will be done to respond to the user.

### 10. Bonus Feature

- One Click Run Script
- Serverless Function on Google Cloud
  - Cloud Functions
- Google PubSub
- Web Interface is hosted on Google Cloud
  - App Engine
- Uploading of Files & Downloading from Google Cloud
  - Google Cloud Storage Bucket
- Audio Input & Output to/from Raspberry Pi
- Asynchronous voice commands to control LED, get sensors value and take picture
  - Pictures are saved at (script location)/picture
- Audio Input & Output is highly customisable. GPIO Pins are customisable too
- Password is hashed for security
- A login system

### 11. Quick-Start Guide

1. Connect a USB audio input
2. Connect a 3.5mm jack audio output
3. Run pi.py
   - `sudo python3 pi.py -u <username> -p <password>`
     - For first time user
   - `sudo python3 pi.py`
4. Hold the button on the Raspberry Pi
5. Start Talking!
6. Release the button to get a reply

To ease the convenience of user, the source code is packaged into one!

- Audio Input MUST be USB
  - Raspberry Pi by default does not have an audio input. The 3.5mm jack only supports audio output.
- Audio Output MUST be 3.5mm jack
  - Through multiple tests, the Raspberry Pi is configured to output audio to only either the 3.5mm jack or Bluetooth. However there is no bluetooth module by default on the pi

### 12. Reference

Amos, D. (2018). *The Ultimate Guide To Speech Recognition With Python – Real Python*. [online] Realpython.com. Available at: https://realpython.com/python-speech-recognition/ [Accessed 20 Jun. 2019].

Pham, H. (n.d.). *PyAudio Documentation — PyAudio 0.2.11 documentation*. [online] People.csail.mit.edu. Available at: https://people.csail.mit.edu/hubert/pyaudio/docs/ [Accessed 20 Jun. 2019].





