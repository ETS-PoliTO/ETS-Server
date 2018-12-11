import paho.mqtt.client as mqtt

import pandas as pd
from copy import deepcopy


class MQTTFakePublisher:
    def __init__(self, config):
        self.config = config

        self.mqttc = mqtt.Client(client_id=config['MQTT_username_fake_publisher'], transport='websockets')
        self.mqttc.on_message = self.on_message
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_subscribe = self.on_subscribe
    
    def on_message(self, mosq, obj, msg):
        pass
    
    def on_connect(self, client, mosq, obj, rc):
        print("Connected to the broker")

    def start(self):
        print("connecting to: ", self.config["MQTT_Broker"], "on port ", self.config["MQTT_Port"])
        self.mqttc.username_pw_set(username=self.config['MQTT_username_fake_publisher'])
        self.mqttc.connect(self.config["MQTT_Broker"], self.config["MQTT_Port"], self.config["Keep_Alive_Interval"])

    def on_subscribe(self):
        pass

    def stop(self):
        self.mqttc.disconnect()
        
    def on_publish(self):
        pass

    def send_buffer(self, buffer, prev_tid):
        # Publishing fake data for each esp
        for i in range(3):
            self.mqttc.publish("ETS/1/"+str(i+1), ("T " + str(prev_tid) + "\n" + buffer[i]))

    def narray_to_string(self, packet):
        string = ""
        for s in packet:
            string = string + " " + str(s)
        return string[1:]

    def fake_pubblish(self, file):
        fd = pd.read_csv(file)
        fd = fd.sort_values(by=['timestamp'])

        buffer = ["", "", ""]
        prevTid = -1

        for packet in fd.get_values()[:50]:
            packet1 = deepcopy(packet)
            packet2 = deepcopy(packet)

            # values of the csv
            # id, MAC, SSID, timestamp, hash, rssi, sn, htci
            #fix this
            id = packet[0]
            mac = packet[1]
            ssid = packet[2]
            timestamp = packet[3]
            hash = packet[4]
            rssi = packet[5]
            sn = packet[6]
            htci = packet[7]

            currTid = int(timestamp) - int(timestamp) % 60

            if currTid > prevTid:
                if prevTid != -1:
                    self.send_buffer(buffer, prevTid)
                    buffer = ["", "", ""]
                prevTid = currTid
            
            # change the id of the ESP
            packet1[0] = (int(id)) % 3 + 1
            packet2[0] = (int(id) + 1) % 3 + 1

            # change the rssi
            packet1[5] = int(rssi) + 10
            packet2[5] = int(rssi) + 15

            i = 0
            for single_packet in packet, packet1, packet2:
                id = int(single_packet[0]) - 1
                buffer[id] = buffer[id] + (self.narray_to_string(single_packet[1:]) + "\n")
                i = i + 1

        # Send the remaining buffer
        self.send_buffer(buffer, prevTid)
