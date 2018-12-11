from copy import deepcopy
from threading import Lock

from data_handling.TimeFrameAnalysis import TimeFrameAnalysis
from utility.utility import getTid


class RoomAnalysis:
    def __init__(self, id, queue, cv, config):
        self.config = config

        # Configuring multiThreading obj
        self.queue = queue
        self.cv = cv
    
        self.roomId = id
        self.currTid = -1
        self.numEsp = config["room"][self.roomId]["numEsp"]
        self.currentAnalysisData = TimeFrameAnalysis(-1, 1, id)

        self.lock = Lock()


    def putData(self, espId, header, rows):
        espTid = getTid(header)
        # DEBUG
        # print("Trying to take the lock for the room: ",self.roomId)
        if espTid < self.currTid:
            print("Old packet, all the packets captured that are written into it will not be be analyzed")
        elif espTid == self.currTid:
            print("for TID: " + str(espTid) + " a the packets was sent, check if it is the last one")
            if self.currentAnalysisData.putRows(espId, header, rows):
                print("for TID: " + str(espTid) + " all the packets were sent, putting it into the queue")
                self.putDataQueue()
                self.currTid += 60
                with self.lock:
                    self.currentAnalysisData = TimeFrameAnalysis(self.currTid, self.numEsp, self.roomId)

        else:
            # The current Time id it's updated, because from now the analysis will be done refering to new Time id
            self.currTid = espTid
            # TODO analyze data with what i have?
            with self.lock:
                self.currentAnalysisData = TimeFrameAnalysis(self.currTid, self.numEsp, self.roomId)
            if self.currentAnalysisData.putRows(espId, header, rows):
                self.putDataQueue()

    def putDataQueue(self):
        with self.cv:
            self.cv.wait(timeout=4)
            with self.lock:
                self.queue.put(deepcopy(self.currentAnalysisData))
            print(self.queue)
            self.cv.notify_all()
