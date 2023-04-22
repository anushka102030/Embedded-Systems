import smbus2
import time
import paho.mqtt.client as mqtt
from datetime import datetime
import mqtt_misc as misc
import ssl

bus = smbus2.SMBus(1)

def convert_to_int(byte_list):
    return (byte_list[0] << 8) + byte_list[1]

def read_A0():
    #request a conversion, and also set the parameters
    bus.write_i2c_block_data(0x48,0x1,[0b11000011, 0b11100011])
    
    #check if the conversion is ready
    conversion_finished = False
    
    while conversion_finished == False:
        config_register = bus.read_i2c_block_data(0x48,0x1,2)
        
        #check that bit 15 is 1 (so it has finished conversion)
        if(config_register[0] & 0x40 != 0):
            conversion_finished = True
            
    #read the result
    read_result = bus.read_i2c_block_data(0x48,0x0,2)
    
    #convert the value to an int
    return convert_to_int(read_result)

def read_A1():
    #request a conversion, and also set the parameters
    bus.write_i2c_block_data(0x48,0x1,[0b11010011, 0b11100011])
    
    #check if the conversion is ready
    conversion_finished = False
    
    while conversion_finished == False:
        config_register = bus.read_i2c_block_data(0x48,0x1,2)
        
        #check that bit 15 is 1 (so it has finished conversion)
        if(config_register[0] & 0x40 != 0):
            conversion_finished = True
        
    #read the result
    read_result = bus.read_i2c_block_data(0x48,0x0,2)
    
    #convert the value to an int
    return convert_to_int(read_result)

#Notes on parameters:
# - alcohol_level is a float
# - air_flow is a float
# - timestamp is an str

  
#subscribes to topic and then writes message
def write_data(client, topic, alcohol_level, timestamp):
    data = "alcohol level: " + str(alcohol_level) + ", timestamp: " + str(timestamp)
    msg_info = client.publish(topic, data)
    res = mqtt.error_string(msg_info.rc)
    #this part doesnt really work 
    print(res)
    if res != "No error.":
        print("Unable to write to server! Error code is ", res) 
    else:
        print ("Successfully written to server:\n", data)
    return res




#run the functions above to write data
if __name__ == '__main__':
    
    while True:
        
        airflow = read_A0()

        if airflow > 8000: #then they're blowing through it
            alcohol = read_A1()
            client = mqtt.Client()
            client.tls_set(ca_certs="mosquitto.org.crt",certfile="client.crt",keyfile="client.key",tls_version=ssl.PROTOCOL_TLSv1_2)
            misc.connectToBroker(client, "test.mosquitto.org", misc.port)
            
            now = datetime.now()
            dt_string = now.strftime("%H:%M")
            write_data(client, "IC.embedded/embreaddedsymptoms/test", alcohol, dt_string)
            misc.disconnect(client)
            time.sleep(60)
        time.sleep(0.1)
