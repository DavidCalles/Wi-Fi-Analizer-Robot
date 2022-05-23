# WiViBot

>Team- Govinda Bhatt, David Calles, Jaskaran Kaur, Alain Reyes


# Project Description

Briefly, our project consists of a small vehicle/robot capable of navigating without crashing. While navigating, it will sense the strength of a given WiFi network, transmit the attained data into a cloud service, and a user interface will provide a graphical representation of the data. The following figure represents a very high level overview of our idea.

![Blocks_Diagram](https://github.com/DavidCalles/Wi-Fi-Analizer-Robot/blob/main/Document_Pictures/ESD-Capstone-BlocksDiagram.drawio.png)
>Blocks Diagram

## Problem Statement

In wider scenarios, a robot with a navigation system could be used for different purposes. From already existing domestics-related robots to self-driving software improvements on conventional vehicles. More specifically, a small self-driving robot with Network connectivity could be used for other more specialized tasks like, room and network mapping, object searching, or security purposes.
Although our project does not cover room or network mapping in its scope, we believe it is a foundation for other more complicated projects, that require the basis of a system like ours.

## Project Requirements

The requirements of the minimum viable product are the following: 

**1 Hardware**

• **MVP:** The robot would make use of a camera module, motors, an ultrasonic sensor, and a Raspberry Pi with a WiFi module. 

• **Nice-to-have features:** The project might also include an external module/antenna for improved WiFi signal acquisition. 

**2 Navigation**

• **MVP:** The robot would move using user input, but will overwrite any instruction to avoid obstacles coming from the front. 

• **Nice-to-have features:** The robot will have a basic self-driving software that avoids collisions and can map the place where the data was recorded. 

**3 Data acquisition** 

• **MVP:** The robot will acquire low quality low frame-rate video, ultrasonic sensor data, and WiFi signal strength of at least 1Hz. 

• **Nice-to-have features:** The robot will acquire higher quality and higher frequency of all the signals stated above.

**4 Web Interface** 

• **MVP:** The data will be represented in a Web dashboard/portal, showing WiFi signal quality in dBm/dB against time in a line graph, along with the video in the corresponding time. 

• **Nice-to-have features:** Additional data can be showed in the dashboard, like mapped position of the vehicle or additional information when hovering over the graphs.

## Team Member Roles/Responsibilities

|Name           |Role				            |Responsibilities		           |
|---------------|-----------------------|------------------------------|
|Govinda Bhatt	|Developer              |Hardware assembly and testing |
|David Calles   |Developer, Team Leader |Navigation related features   |
|Jaskaran Kaur  |Developer, Recorder    |Web Interface				         |
|Alain Reyes  	|Developer		          |Data acquisition              |
