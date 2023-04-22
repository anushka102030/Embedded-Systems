import paho.mqtt.client as mqtt
from datetime import date
from csv import DictWriter
import mqtt_misc as misc
import ssl
# import json

BASE_PATH = "Readings_data/"
FILENAME = "Alcolock.csv"

# def on_connect(client, userdata, flags, rc):
#     if rc == 0:
#         print("Connected OK!")
#     else:
#         print("Bad connection! Return code: ", str(rc))


#here it will write to file
def on_message(client, userdata, msg):
    try:
        data = msg.payload.decode()
        print(data)
        Dict = dict((x.strip(), y.strip())
             for x, y in (element.split(': ')
             for element in data.split(', ')))
        #Write dictionary to a csv file
        with open(BASE_PATH + FILENAME, "a+", newline = '') as f:
            #We obtain the keys in the dictionary as a list - these will be the fieldnames inthe csv file.
            field_names = list(Dict.keys())
            #Perform the write to the file
            writer = DictWriter(f, fieldnames=field_names)
            writer.writerow(Dict)

        if data == "goodbye":
            misc.disconnect(client)
        #return success code and message
        return "Success", 200

    # Account for Exception
    except Exception as e:
        #return error code and exceotion message.
        return str(e), 404


def read_data(client):
    # client.on_connect = misc.on_connect
    client.subscribe("IC.embedded/embreaddedsymptoms/test")
    client.on_message = on_message

    client.loop_forever()


if __name__ == '__main__':
    client = mqtt.Client()
    client.tls_set(ca_certs="mosquitto.org.crt",certfile="client.crt",keyfile="client.key",tls_version=ssl.PROTOCOL_TLSv1_2)
    misc.connectToBroker(client, "test.mosquitto.org", misc.port)
    read_data(client)
