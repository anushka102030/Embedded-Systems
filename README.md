# AlcoLock (version for Windows)

AlcoLock is an IoT system. It blocks a laptop's access to a pre-set list of websites when the user is drunk i.e. a high level of alcohol in his/her breath. This is potentially useful to prevent irresponsible spending of money online, undesirable behaviour on social media/messaging platforms and other people using the laptop of the drunk person.

It consists of a remote  breathalyser which a user blows into at regular intervals. The breathalyser readings are sent to a desktop application on the laptop (over MQTT). This application then blocks sites based on the level of alcohol in the user's breath. The application GUI displays a user's alcohol level over time on a graph display. It has a feature that allows a user to configure the sending of emails to people when very drunk. This allows the user to call in sick for work tomorrow at the click of a button.



## Website:
  https://alcolock494991639.wordpress.com
  
## Marketing Video:

https://www.youtube.com/watch?v=3BMfqGLoMrM&feature=youtu.be

## A Description of the Project

The project has two components - the **breathalyser** and the **desktop application**.

The breathalyser is a embedded device developed from a raspberry Pi. It has an airflow sensor ([Omron D6F-V03A1](https://in.element14.com/omron/d6f-v03a1/sensors-air-velocity-mems-0-3mps/dp/1573149)) and a sensor that measures the alcohol content in air ([MQ-3 alcohol detector](https://www.teachmemicro.com/mq-3-alcohol-sensor/)). These sensors send readings to the Pi via I2C. The breathalyser device looks like this: 

<img src="https://user-images.githubusercontent.com/56508438/109037873-1b151980-76c3-11eb-866b-d891330e50bf.jpg" alt="drawing" width="400" height="400"/>

A user would blow into a hole. When the air-flow is fast enough, the breathalyser will send its reading of the alcohol level in the user's breath to the desktop application. Communication is via [MQTT](https://en.wikipedia.org/wiki/MQTT) - the MQTT broker can be found [here](http://test.mosquitto.org/). We also use the [HiveMQ MQTT client](https://www.hivemq.com/blog/full-featured-mqtt-client-browser/). Communication is encrypted with TLS.

The desktop application will run on the user's laptop. It has a GUI as illustrated below:

<img src="https://user-images.githubusercontent.com/56508438/109037748-fb7df100-76c2-11eb-99fe-17c0c24a994b.jpg" alt="drawing" width="400" height="400"/>

The GUI plots the measured alcohol level versus a timestamp and updates when new readings arrive. It blocks pre-defined lists of sites based on the region in which the readings are falling (see the part on *Drunkenness Levels* under *How to Run the Application*). It allows users to call in sick for work tomorrow by offering a fully configurable auto-email sending system. It allows users to keep track of water intake and find suggestions on how to avoid a hangover. For more information, see *How to Run the Application*.


## How to Set Things Up

The project folder *Desktop Application* has the code that will run on the user's laptop. The folder *Raspberry Pi* has the code that runs on the embedded device i.e the breathalyser.

### Embedded Device (Breathalyser)

**Prerequisites:** The breathalyser is a Raspberry Pi connected to two sensors. It is enclosed in a plastic case (see the diagram above). Raspberry Pi's come with python3 installed. In addition to python standard libraries, two additional modules are installed on the Pi for the breathalyser to work. These are:
 - *paho-mqtt* (for communication with the computer)
 - *smbus* (for i2c communication with the sensors)

Additionally TLS certificates have to be set up with the Mosquitto server. The details of this are not discussed here. 

### Desktop Application 

**Prerequisites:**  *Python* must be installed for these programs to run on the laptop. In addition to python standard libraries, some additional modules need to be installed. These are:
 - *paho-mqtt* (for communication with the breathalyser)
 - *matplotlib* (to plot the graphs)
 - *numpy* (for fast calculations)
 - *pandas* (for loading data)
 - *pysimplegui* (for displaying the desktop application)
 - *pillow* (for graphics/image processing)

If [*pip*](https://www.w3schools.com/python/python_pip.asp) is installed and the system is Windows, running the *install-dependencies.bat* script (see folder *Desktop Application*) once the application is downloaded will download all of these libraries onto your system in one go. This application is designed for Windows but can be adapted for MacOS or Linux (See "Adapting for other OS" athe the end).

The project can be downloaded from this repo. Once this is done and the dependencies are installed, you can configure emails and sites to block. Navigate to *Desktop Application/Emails* and *Desktop Application/blocker* for user guides on how to modify the configuration files.


## How to Run the Application

### Embedded Device (Breathalyser)

Run the *pi_client.py* file on the Raspberry Pi. This will start the program which will send a message through MQTT every time that the user blows into the device. **A good practice is to blow into the device at a maximum frequency of once every five minutes**.
 
### Desktop Application 

To run the application, double click on *Desktop Application/run.bat*. This is a batch script that you can also run from the command line. You will be asked for permission for the program to run in admin mode ("Do you want to allow command prompt to make changes to your device?"). You must click "yes", so that the website blocking can be implemented.

Blowing into the breathalyser will send a new reading to the application. **A good practice is to aim to send readings at a maximum frequency of once every five minutes**.

The graph will update with new readings every time you have the Alcolock window open and you press a key on the keyboard. You can click on the glass icon - this will update a progress bar that shows how many glasses of water you have drunk. Clicking on "How to sober up" will open Google Chrome (if you have it installed) and display a site with tips on how to ameliorate a hangover. Clicking on "Close" in the bottom left corner will result in emails being sent if Alcolock thinks you are "very drunk" (see the part on "Drunkenness Levels"). Closing the display via the top right icon will close the application without sending emails.

A command line window will also open when you run the application. This allows you to keep track of what is going on behind the scenes.

**Drunkenness Levels:** The app has three levels of drunkenness:
- *Not Drunk*: The user is sober and no sites are blocked. Emails will not be sent on pressing "Close". This is the green region of the graph.
- *Slightly Drunk*: The user has a detectable level of alcohol which may affect behaviour. A specific list of sites (*medium.txt*) is blocked, but emails are not sent. This corresponds to the yellow region of the graph display.
- *Very Drunk*: The user's breath has high levels of alcohol - there is a high probability of irresponsible behaviour. A specific list of sites (*sites.txt*) is blocked. Emails are sent to the listed recipients on pressing "Close". The user's alcohol level would be in the red region of the graph.


## Future Developments

The app can be extended to MacOS and Linux systems (see next section). We also plan to bring AlcoLock to mobile!

## Adapting for Other OS
- **Path of the Hosts File**: The application modifies the [hosts file](https://en.wikipedia.org/wiki/Hosts_(file)) on a laptop. Currently, the HOSTSPATH variable in *Desktop Application/blocker/website_control.py* is set to "C:\Windows\System32\drivers\etc\hosts" - the path of the hosts file on windows OS. This needs to be changed for MacOS/Linux (generally the path in these systems is "etc\hosts").
- **Scripts**: The batch scripts *run.bat* and *install-dependencies.bat* only work on Windows. On MacOS/Linux, these can be replaced by bash scripts, although we have not implemented these.
- **Admin Mode**: While the programs run in admin mode for Windows, they must be run with [sudo permissions](https://en.wikipedia.org/wiki/Sudo) in Linux/MacOS.

## Contributors
- [Anushka Kulkarni](https://github.com/anushka102030)
+ [Rishil Patel](https://github.com/r15hil)
* [Aaman Rebello](https://github.com/aamanrebello)
- [Victor Florea](https://github.com/VFjr)

