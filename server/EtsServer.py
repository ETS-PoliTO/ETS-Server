from queue import Queue
from threading import Lock, Condition, Thread
from time import sleep

from analysis.Analyzer import Analyzer
from mqtt import MQTTFakePublisher
from mqtt import MQTTListener


def run_mqtt(mqttclient):
    mqttclient.start()
    #mqttclient.loop()


def run_mqtt_fake(mqttclient):
    mqttclient.start()
    mqttclient.fake_pubblish("mqtt/sample_fakedata_1.csv")


class EtsServer:
    def __init__(self, config, fake=False, db_persistence=False):

        # variables for multithreading
        self.q = Queue()
        self.cv = Condition()
        self.fake = fake

        # classes
        self.mqttl = MQTTListener(self.q, self.cv, config)
        self.analyzer = Analyzer(self.q, self.cv, config, db_persistence)
        if fake:
            self.mqttfp = MQTTFakePublisher(config)

        # threads
        self.thread_mqttl = Thread(target=run_mqtt, args=(self.mqttl,))
        if fake:
            self.thread_mqttfp = Thread(target=run_mqtt_fake, args=(self.mqttfp,))

    def start(self):
        self.analyzer.start()
        self.thread_mqttl.start()
        if self.fake:
            sleep(1)
            self.thread_mqttfp.start()

    def stop(self):
        # we declare to stop everything
        self.analyzer.stop()
        self.mqttl.stop()
        if self.fake:
            self.mqttfp.stop()

        # join threads
        if self.fake:
            self.thread_mqttfp.join()
        self.thread_mqttl.join()

