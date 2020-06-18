import hashlib
import os
import threading

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication, QGridLayout, QFrame, QLineEdit, QPushButton, QSizePolicy, QRadioButton, QComboBox, QFileDialog, QCheckBox

from Core.HashAndCompareInputFiles import HashAndCompareInputFiles


class MainWindow(QMainWindow):
    def __init__(self, ScriptName, AbsoluteDirectoryPath):
        # Store Parameters
        self.ScriptName = ScriptName
        self.AbsoluteDirectoryPath = AbsoluteDirectoryPath

        # Variables
        self.ComparisonInProgress = False
        self.LastSelectedFilePath = None

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
        self.WindowIcon = QIcon(self.GetResourcePath("Assets/SerpentHash Icon.png"))

        # Window Icon and Title
        self.setWindowIcon(self.WindowIcon)
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
        self.IgnoreNamesInFileModeCheckBox = QCheckBox("Ignore names in file mode?")
        self.IgnoreNamesInFileModeCheckBox.setChecked(True)

        self.AlgorithmComboBox = QComboBox()
        self.AlgorithmComboBox.setEditable(False)
        self.PopulateAlgorithmList()

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

        self.CompareHashesButton = QPushButton("Compare Hashes")
        self.CompareHashesButton.clicked.connect(self.CompareHashes)
        self.CompareHashesButton.setSizePolicy(self.ButtonAndLineEditSizePolicy)

        # Create Layout
        self.Layout = QGridLayout()

        # Widgets in Layout
        self.Layout.addWidget(self.FolderModeRadioButton, 0, 0, Qt.AlignRight)
        self.Layout.addWidget(self.FileModeRadioButton, 0, 1)
        self.Layout.addWidget(self.IgnoreNamesInFileModeCheckBox, 0, 2)
        self.Layout.addWidget(self.AlgorithmComboBox, 0, 3)
        self.Layout.addWidget(self.FileOneLineEdit, 1, 0, 1, 3)
        self.Layout.addWidget(self.FileOneSelectButton, 1, 3)
        self.Layout.addWidget(self.FileTwoLineEdit, 2, 0, 1, 3)
        self.Layout.addWidget(self.FileTwoSelectButton, 2, 3)
        self.Layout.addWidget(self.CompareHashesButton, 3, 0, 1, 4)

        # Set and Configure Layout
        self.Layout.setColumnStretch(0, 1)
        self.Layout.setColumnStretch(1, 1)
        self.Layout.setColumnStretch(2, 1)
        self.Layout.setRowStretch(3, 1)
        self.Frame.setLayout(self.Layout)

        # Create Status Bar
        self.StatusBar = self.statusBar()

        # Set Central Frame
        self.setCentralWidget(self.Frame)

    def GetResourcePath(self, RelativeLocation):
        return self.AbsoluteDirectoryPath + "/" + RelativeLocation

    def ClearInput(self):
        self.FileOneLineEdit.clear()
        self.FileTwoLineEdit.clear()
        self.LastSelectedFilePath = None

    def PopulateAlgorithmList(self):
        AvailableAlgorithms = sorted(hashlib.algorithms_available)
        self.AlgorithmComboBox.addItems(AvailableAlgorithms)
        DefaultAlgorithmOptions = ("md5", "sha1")
        DefaultAlgorithm = None
        for DefaultAlgorithmOption in DefaultAlgorithmOptions:
            if DefaultAlgorithmOption in AvailableAlgorithms:
                DefaultAlgorithm = DefaultAlgorithmOption
                break
        if DefaultAlgorithm is not None:
            self.AlgorithmComboBox.setCurrentText(DefaultAlgorithm)

    def SelectFile(self, FileLineEdit):
        CurrentPath = ""
        if self.LastSelectedFilePath is not None:
            LastSelectedFilePathDirectory = os.path.dirname(self.LastSelectedFilePath)
            if os.path.exists(LastSelectedFilePathDirectory):
                CurrentPath = LastSelectedFilePathDirectory
        if self.FolderModeRadioButton.isChecked():
            Selected = QFileDialog.getExistingDirectory(caption="Select Folder", directory=CurrentPath)
        else:
            Selected = QFileDialog.getOpenFileName(caption="Select File", directory=CurrentPath)[0]
        if Selected != "":
            FileLineEdit.setText(Selected)
            self.LastSelectedFilePath = Selected

    def CompareHashes(self):
        FileOne = self.FileOneLineEdit.text()
        FileTwo = self.FileTwoLineEdit.text()

        # Validate Inputs
        if FileOne == "" or FileTwo == "":
            self.DisplayMessageBox("Two files must be selected to compare.")
            return
        if not (os.path.exists(FileOne) and os.path.exists(FileTwo)):
            self.DisplayMessageBox("At least one file does not exist.", Icon=QMessageBox.Warning)
            return
        if FileOne == FileTwo:
            self.DisplayMessageBox("Must select different files to compare.")
            return

        # Set Status Bar
        self.StatusBar.showMessage("Comparison in progress...")

        # Check Whether to Ignore File Names
        if self.FileModeRadioButton.isChecked() and self.IgnoreNamesInFileModeCheckBox.isChecked():
            IgnoreNames = True
        else:
            IgnoreNames = False

        # Compare
        self.ComparisonInProgress = True
        ComparisonThreadInst = ComparisonThread(FileOne, FileTwo, Algorithm=self.AlgorithmComboBox.currentText(), IgnoreSingleFileNames=IgnoreNames)
        ComparisonThreadInst.ComparisonDoneSignal.connect(lambda: self.DisplayResult(ComparisonThreadInst))
        ComparisonThreadInst.start()

    def DisplayResult(self, ComparisonThread):
        # Clear In-Progress
        self.ComparisonInProgress = False
        self.StatusBar.clearMessage()

        # Get Result
        FilesIdentical = ComparisonThread.Result

        # Display Result
        if FilesIdentical is None:
            self.DisplayMessageBox("An error occurred.  Files were not compared.", Icon=QMessageBox.Warning)
        elif FilesIdentical:
            self.DisplayMessageBox("Files are identical!")
        else:
            self.DisplayMessageBox("Files are not identical!", Icon=QMessageBox.Warning)

    def closeEvent(self, event):
        if self.ComparisonInProgress:
            if self.DisplayMessageBox("A comparison is in progress.  Exit anyway?", Icon=QMessageBox.Question, Buttons=(QMessageBox.Yes | QMessageBox.No)) == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    # Interface Methods
    def DisplayMessageBox(self, Message, Icon=QMessageBox.Information, Buttons=QMessageBox.Ok, Parent=None):
        MessageBox = QMessageBox(self if Parent is None else Parent)
        MessageBox.setWindowIcon(self.WindowIcon)
        MessageBox.setWindowTitle(self.ScriptName)
        MessageBox.setIcon(Icon)
        MessageBox.setText(Message)
        MessageBox.setStandardButtons(Buttons)
        return MessageBox.exec_()

    # Window Management Methods
    def Center(self):
        FrameGeometryRectangle = self.frameGeometry()
        DesktopCenterPoint = QApplication.primaryScreen().availableGeometry().center()
        FrameGeometryRectangle.moveCenter(DesktopCenterPoint)
        self.move(FrameGeometryRectangle.topLeft())


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

    def start(self):
        self.Thread.start()

    def run(self):
        self.Result = HashAndCompareInputFiles(self.InputOne, self.InputTwo, Algorithm=self.Algorithm, IgnoreSingleFileNames=self.IgnoreSingleFileNames)
        self.ComparisonDoneSignal.emit()
