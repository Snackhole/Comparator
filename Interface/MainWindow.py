from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication, QGridLayout, QFrame, QLineEdit, QPushButton, QSizePolicy, QRadioButton


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

        # Button and Line Edit Size Policy
        self.ButtonAndLineEditSizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        # Create Central Frame
        self.Frame = QFrame()

        # Create Widgets
        self.FolderModeRadioButton = QRadioButton("Folder Mode")
        self.FolderModeRadioButton.setChecked(True)
        self.FolderModeRadioButton.toggled.connect(self.ClearInput)
        self.FileModeRadioButton = QRadioButton("File Mode")
        self.FileModeRadioButton.toggled.connect(self.ClearInput)

        self.FileOneLineEdit = QLineEdit()
        self.FileOneLineEdit.setReadOnly(True)
        self.FileOneLineEdit.setPlaceholderText("First file to compare...")
        self.FileOneLineEdit.setMinimumWidth(250)
        self.FileOneLineEdit.setSizePolicy(self.ButtonAndLineEditSizePolicy)

        self.FileTwoLineEdit = QLineEdit()
        self.FileTwoLineEdit.setReadOnly(True)
        self.FileTwoLineEdit.setPlaceholderText("Second file to compare...")
        self.FileTwoLineEdit.setMinimumWidth(250)
        self.FileTwoLineEdit.setSizePolicy(self.ButtonAndLineEditSizePolicy)

        self.FileOneSelectButton = QPushButton("Select")
        self.FileOneSelectButton.clicked.connect(lambda: self.SelectFile(self.FileOneLineEdit))
        self.FileOneSelectButton.setSizePolicy(self.ButtonAndLineEditSizePolicy)
        self.FileTwoSelectButton = QPushButton("Select")
        self.FileTwoSelectButton.clicked.connect(lambda: self.SelectFile(self.FileTwoLineEdit))
        self.FileTwoSelectButton.setSizePolicy(self.ButtonAndLineEditSizePolicy)

        self.HashAndCompareButton = QPushButton("Hash and Compare")
        self.HashAndCompareButton.clicked.connect(self.HashAndCompare)
        self.HashAndCompareButton.setSizePolicy(self.ButtonAndLineEditSizePolicy)

        # Create Layout
        self.Layout = QGridLayout()

        # Widgets in Layout
        self.Layout.addWidget(self.FolderModeRadioButton, 0, 0, Qt.AlignRight)
        self.Layout.addWidget(self.FileModeRadioButton, 0, 1)
        self.Layout.addWidget(self.FileOneLineEdit, 1, 0, 1, 2)
        self.Layout.addWidget(self.FileOneSelectButton, 1, 2)
        self.Layout.addWidget(self.FileTwoLineEdit, 2, 0, 1, 2)
        self.Layout.addWidget(self.FileTwoSelectButton, 2, 2)
        self.Layout.addWidget(self.HashAndCompareButton, 3, 0, 1, 3)

        # Set and Configure Layout
        self.Layout.setColumnStretch(0, 1)
        self.Layout.setColumnStretch(1, 1)
        self.Layout.setRowStretch(3, 1)
        self.Frame.setLayout(self.Layout)

        # Create Status Bar
        self.StatusBar = self.statusBar()

        # Set Central Frame
        self.setCentralWidget(self.Frame)

        # Initial Focus

    def GetResourcePath(self, RelativeLocation):
        return self.AbsoluteDirectoryPath + "/" + RelativeLocation

    def ClearInput(self):
        self.FileOneLineEdit.clear()
        self.FileTwoLineEdit.clear()

    def SelectFile(self, FileLineEdit):
        pass

    def HashAndCompare(self):
        pass

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
