import threading

from PyQt5 import QtCore


class StatusThread(QtCore.QObject):
    UpdateProgressSignal = QtCore.pyqtSignal()

    def __init__(self, HashThreadOne, HashThreadTwo):
        super().__init__()
        self.HashThreadOne = HashThreadOne
        self.HashThreadTwo = HashThreadTwo
        self.Thread = threading.Thread(target=self.run, daemon=True)

    def start(self):
        self.Thread.start()

    def run(self):
        while not self.HashThreadOne.HashComplete and not self.HashThreadTwo.HashComplete:
            self.UpdateProgressSignal.emit()
