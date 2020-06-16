from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication, QGridLayout, QFrame, QLineEdit, QPushButton


class MainWindow(QMainWindow):
    def __init__(self, ScriptName, AbsoluteDirectoryPath):
        # Store Parameters
        self.ScriptName = ScriptName
        self.AbsoluteDirectoryPath = AbsoluteDirectoryPath

        # Initialize
        super().__init__()

        # Create Interface
        self.CreateInterface()

        # Center Window
        self.Center()

        # Show Window
        self.show()

    def CreateInterface(self):
        # Create Window Icon
        # self.WindowIcon = QIcon(self.GetResourcePath("Assets/SerpentHash Icon.png"))

        # Window Icon and Title
        # self.setWindowIcon(self.WindowIcon)
        self.setWindowTitle(self.ScriptName)

        # Create Central Frame
        self.Frame = QFrame()

        # Create Widgets
        self.InputOneLineEdit = QLineEdit()
        self.InputOneLineEdit.setReadOnly(True)
        self.InputOneLineEdit.setPlaceholderText("First File")

        self.InputTwoLineEdit = QLineEdit()
        self.InputTwoLineEdit.setReadOnly(True)
        self.InputTwoLineEdit.setPlaceholderText("Second File")

        self.InputOneSelectButton = QPushButton("Select")
        self.InputTwoSelectButton = QPushButton("Select")

        self.HashAndCompareButton = QPushButton("Hash and Compare")

        # Create Layout
        self.Layout = QGridLayout()
        self.Frame.setLayout(self.Layout)

        # Widgets in Layout
        self.Layout.addWidget(self.InputOneLineEdit, 0, 0)
        self.Layout.addWidget(self.InputOneSelectButton, 0, 1)
        self.Layout.addWidget(self.InputTwoLineEdit, 1, 0)
        self.Layout.addWidget(self.InputTwoSelectButton, 1, 1)
        self.Layout.addWidget(self.HashAndCompareButton, 2, 0, 1, 2)

        # Create Status Bar
        self.StatusBar = self.statusBar()

        # Set Central Frame
        self.setCentralWidget(self.Frame)

        # Initial Focus

    def GetResourcePath(self, RelativeLocation):
        return self.AbsoluteDirectoryPath + "/" + RelativeLocation

    # Interface Methods
    def DisplayMessageBox(self, Message, Icon=QMessageBox.Information, Buttons=QMessageBox.Ok, Parent=None):
        MessageBox = QMessageBox(self if Parent is None else Parent)
        MessageBox.setWindowIcon(self.WindowIcon)
        MessageBox.setWindowTitle(self.ScriptName)
        MessageBox.setIcon(Icon)
        MessageBox.setText(Message)
        MessageBox.setStandardButtons(Buttons)
        return MessageBox.exec_()

    def FlashStatusBar(self, Status, Duration=2000):
        self.StatusBar.showMessage(Status)
        QTimer.singleShot(Duration, self.StatusBar.clearMessage)

    # Window Management Methods
    def Center(self):
        FrameGeometryRectangle = self.frameGeometry()
        DesktopCenterPoint = QApplication.primaryScreen().availableGeometry().center()
        FrameGeometryRectangle.moveCenter(DesktopCenterPoint)
        self.move(FrameGeometryRectangle.topLeft())
