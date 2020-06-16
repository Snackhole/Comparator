from PyQt5.QtWidgets import QMainWindow


class MainWindow(QMainWindow):
    def __init__(self, ScriptName, AbsoluteDirectoryPath):
        # Store Parameters
        self.ScriptName = ScriptName
        self.AbsoluteDirectoryPath = AbsoluteDirectoryPath

        # Initialize
        super().__init__()

        # Create Interface
        self.CreateInterface()
        self.show()

    def CreateInterface(self):
        pass
