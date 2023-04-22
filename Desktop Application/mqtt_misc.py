import paho.mqtt.client as mqtt

port = 8883

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected OK!")
    else:
        print("Bad connection! Return code: ", str(rc))

#broker is mosquitto 
def connectToBroker(client, BROKER_ADDRESS, N): 
    client.connect(BROKER_ADDRESS, port=N)
    client.on_connect = on_connect


def disconnect(client):
    client.disconnect()
    print("Successfully disconnected!")