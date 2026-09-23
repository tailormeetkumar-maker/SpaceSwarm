"""Earth control/analysis facade."""

from Earth.data_receiver import EarthDataReceiver
from Earth.earth_algorithm import summarize


class Earth:
    def __init__(self):
        self.receiver = EarthDataReceiver()

    def receive(self, message):
        return self.receiver.receive(message)

    def summary(self):
        return summarize(self.receiver)
