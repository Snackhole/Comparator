import threading

from PyQt5 import QtCore

from Core.HashAndCompareInputFiles import HashAndCompareInputFiles


class ComparisonThread(QtCore.QObject):
    ComparisonDoneSignal = QtCore.pyqtSignal()

    def __init__(self, InputOne, InputTwo, Algorithm=None, IgnoreSingleFileNames=False):
        super().__init__()
        self.InputOne = InputOne
        self.InputTwo = InputTwo
        self.Algorithm = Algorithm
        self.IgnoreSingleFileNames = IgnoreSingleFileNames
        self.Result = None
        self.Thread = threading.Thread(target=self.run, daemon=True)
        self.ComparisonDone = False

    def start(self):
        self.Thread.start()

    def run(self):
        self.Result = HashAndCompareInputFiles(self.InputOne, self.InputTwo, Algorithm=self.Algorithm, IgnoreSingleFileNames=self.IgnoreSingleFileNames)
        self.ComparisonDone = True
        self.ComparisonDoneSignal.emit()
