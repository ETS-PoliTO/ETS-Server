from data_handling.RoomAnalysis import RoomAnalysis
from threading import Lock

class DataHandler:
    def __init__(self, queue, cv, config):
        # configurations
        self.queue = queue
        self.cv = cv

        self.config = config
        self.numRoom = config["numRoom"]
        self.roomsConf = config["room"]

        self.lock = Lock()
        self.rooms = dict()
    
    def put(self, topic, payload):
        #DEBUG
        print(" ")
        print("MQTT Data Received...")
        print("MQTT Topic: " + topic)
        print("Data: " + payload)
        print("")

        roomId, espId = topic.split("/")[1:3]
        # topic ETS\%room\%esp:
        if roomId not in self.rooms:
            self.rooms[roomId] = RoomAnalysis(roomId, self.queue, self.cv, self.config)
        allRows = payload.split('\n')
        allRowsFiltered = list(filter(lambda x: x != "", allRows))
        header = allRowsFiltered[0]
        self.rooms[roomId].putData(espId, header, allRowsFiltered[1:])
