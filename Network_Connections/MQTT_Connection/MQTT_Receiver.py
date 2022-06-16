
import paho.mqtt.client as mqtt #import the client1
import time

my_host = "broker.hivemq.com"
my_port = 1883
my_topic = "WIFI_Robot_Analizer_DC"
my_qos = 2

data = []
receivingDataFlag = False

# Handshake messages
expectedStart = 'Start Data'
expectedEnd = 'End Data'

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")
    else:
        print("Client disconnected. ")
    client.loop_stop()

# CALLBACK FUNCTION FOR MQTT CONNECTION TO BROKER 
def on_connect(client, userdata, flags, rc):
    print(f'connected {client._client_id}')
    client.subscribe(topic=my_topic, qos=my_qos)
    client.publish(my_topic, payload="Device Suscribed: "+str(client._client_id), qos=my_qos)

# CALLBACK FUNCTION FOR MQTT  RECEIVED MESSAGE 
    # EVALUATE received messages
def on_message(client, userdata, message):
    global data
    msg = message.payload.decode()
    print("Mqtt message: ", msg)
 
    if(msg[0:7] == 'Sample,'):
        data.append(msg[7:])

# HANDSHAKE FUNCTION

class NewMQTTReceiver:
    
    def __init__(self, clientId, segs):
        self.client = mqtt.Client(client_id=clientId)#my_clientid
        self.client.on_connect = on_connect
        self.client.on_message = on_message
        self.client.on_disconnect = on_disconnect
        self.client.connect(host=my_host, port=my_port)
        self.client.loop_start()
        time.sleep(segs)
    
    def publish(self, payload):
        self.client.publish(my_topic, payload=payload, qos=my_qos)
    
    def disconnect(self):
        self.client.disconnect()  
        self.client.loop_stop()  
    
 

