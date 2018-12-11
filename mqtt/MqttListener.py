import paho.mqtt.client as mqtt

from data_handling.DataHandler import DataHandler


class MQTTListener():
    def __init__(self, queue, cv, config):
        self.config = config
        print("Creating MQTT Obj")
        
        # the data handler is initialized
        self.dataHandler = DataHandler(queue, cv, config)

        # mqtt client is configured
        self.mqttc = mqtt.Client(client_id=self.config['MQTT_username_listener'], transport='websockets')
        self.mqttc.on_message = self.on_message
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_subscribe = self.on_subscribe


    # Subscribe to all Sensors at Base Topic
    def on_connect(self, mqttc, obj, flags, rc):
        mqttc.subscribe(self.config["MQTT_Topic"], 0)
        print("Connected to " + self.config["MQTT_Broker"] + " on port: " + str(self.config["MQTT_Port"]))
    
    def on_subscribe(self, mosq, obj, mid, granted_qos):
        print("Client successfully subscribed to topic")

    def on_message(self, mosq, obj, msg):
        self.dataHandler.put(str(msg.topic), str(msg.payload.decode("UTF-8")))

    def start(self):
        # Connect
        print("connecting to: ", self.config["MQTT_Broker"], "on port ", self.config["MQTT_Port"])
        self.mqttc.username_pw_set(username=self.config['MQTT_username_listener'])
        self.mqttc.connect(self.config["MQTT_Broker"], self.config["MQTT_Port"], self.config["Keep_Alive_Interval"])
        self.mqttc.loop_forever()

    def stop(self):
        self.mqttc.disconnect()
        self.mqttc.loop_stop()

    def loop(self):
        while self.mqttc.loop() == 0:
            pass

