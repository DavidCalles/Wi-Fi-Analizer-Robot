
import paho.mqtt.client as mqtt #import the client1

my_host = "broker.hivemq.com"
my_port = 1883
my_topic = "WIFI_Robot_Analizer_DC"
my_qos = 2

# Handshake messages
expectedHelloFromPc = "PC says: Hi my dude"
helloFromRpi = "RPi says: Hi my dude"

expectedByeFromPc = "PC says: Bye my dude"
byeFromRpi = "RPi says: Bye my dude"

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")
    else:
        print("Client disconnected. ")

# CALLBACK FUNCTION FOR MQTT CONNECTION TO BROKER 
def on_connect(client, userdata, flags, rc):
    print('connected (%s)' % client._client_id)
    client.subscribe(topic=my_topic, qos=my_qos)
    client.publish(my_topic, payload="Device Suscribed", qos=my_qos)

# CALLBACK FUNCTION FOR MQTT  RECEIVED MESSAGE 
    # EVALUATE received messages
def on_message(client, userdata, message):
    msg = message.payload.decode()
    print("MESSAGE: ", msg)
    if(msg == expectedHelloFromPc):
        print("New PC detected!")
    
    if(msg == expectedByeFromPc):
        client.publish(my_topic, payload=byeFromRpi, qos=my_qos)
        print ("CONNECTION WITH PC STABLISHED SUCCESFULLY!")
        client.disconnect()    

# HANDSHAKE FUNCTION

class NewMQTTConnection:
    
    def __init__(self, clientId):
        self.client = mqtt.Client(client_id=clientId)#my_clientid
        self.client.on_connect = on_connect
        self.client.on_message = on_message
        self.client.on_disconnect = on_disconnect
        self.client.connect(host=my_host, port=my_port)
        self.client.loop_forever()
    
    def publish(self, payload):
        self.client.publish(my_topic, payload=payload, qos=my_qos)
    
    def disconnect(self):
        self.client.disconnect()    
    
 

