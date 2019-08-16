# Tutorial Documentation of Heypi 

## Project Description

Heypi is a project done as an experiment which has a voice chat system that utilizes cloud services to carry out its functions. With the implementation of IOT products such as DHT and light sensors Heypi is able to offer more than just a typical voice chat application. Real time reports of the temperature and light can be seen, in future implementation of heypi we can make both end users of the application understand the other client's environment more. 

A Youtube link of our project can be found at 

```
<a href="" target="_blank"><img src="http://img.youtube.com/vi/YOUTUBE_VIDEO_ID_HERE/0.jpg" 
alt="IMAGE ALT TEXT HERE" width="240" height="180" border="10" /></a>
```

### 1. Setting up the Raspberri pi

Setting up of the Raspberri pi is rather straight forward. The end result of this section will be something like this

![Finished](/images/finished.jpg?raw=true)

Do ensure the following sensors, resistors and amount of cables are present before setting up

- 1 x DHT 11 Sensor
- 1 x LED 
- 1 x  MCP3008 ADC
- 1 x  Light sensitive resistor
- 1 x button
- 2 x Resistor  10k ohms
- 2 x Resistor 330 ohms 
- 22 x wires 

A fritzing.jpg attached on this github. The exact replication will be required to be setup in order for the application to work without any issues.

![Fritzing diagram](/images/Fritzing.png?raw=true)

### 2. Installation of required Modules

* Required apt-get modules
  * adafruit_dht
  - espeak
  - mosquitto mosquitto-clients
  - python3
  - python3-dev
  - python3-pyaudio
* Required pip3 modules
  * adafruit_dht
  - contextlib2
  - cryptography
  - espeak
  - flaky
  - flask
  - gcp-devrel-py-tools
  - google-auth
  - google-auth-httplib2
  - google-cloud-pubsub
  - google-cloud-storage
  - google-cloud-tools
  - gpiozero
  - mysql-connector-python
  - oauth2
  - oauth2Client
  - picamera
  - pyjwt
  - wave

### 3. Running the Software

1. Run the pi.py application with the following arguments **e.g (pi.py -u user - p password123)** The application will automatically generate an RSA key and establish as well as create an account on our web **Do note the password and username entered will be used on the web interface later.**
2. Log onto the web interface at http://heypi-iot.appspot.com/login
3. Voice Record function
   - Press and Hold button
   - Speak into mic
   - Release the button
4. Once the voice message is recorded the program will upload it into the cloud storage and all other pi subscribed to the MQTT topic will receive and download the voice file from the cloud storage
5. Dashboard will update itself periodically based on the MQTT transmissions from the pi. 
6. An LED can be turned on and off on the dashboard by clicking.