from Earth.earth_communication import EarthCommunication
from Earth.earth_algorithm import EarthAlgorithm
from Earth.data_receiver import DataReceiver
from Earth.ml_analysis import MLAnalyzer

class Earth:
    def __init__(self):
        self.communication = EarthCommunication()
        self.algorithm = EarthAlgorithm()
        self.receiver = DataReceiver()
        self.ml = MLAnalyzer()
        self.messages_received = 0
        self.discovery_archive = self.receiver.discovery_archive

    def update(self, mothers: list) -> list:
        messages = self.communication.receive_all()
        self.messages_received += len(messages)
        discoveries = self.receiver.process(messages)
        for mother, command in self.algorithm.evaluate(discoveries, mothers):
            self.communication.send_to_mother(mother, command)
        return discoveries
