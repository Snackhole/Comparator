import copy
import hashlib
import json
import os
import threading
from math import floor

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPalette, QColor, QAction
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QApplication, QGridLayout, QFrame, QLineEdit, QPushButton, QSizePolicy, QRadioButton, QComboBox, QFileDialog, QCheckBox, QProgressBar, QLabel, QInputDialog

from Interface.Threads.ComparisonThread import ComparisonThread
from Interface.Threads.StatusThread import StatusThread


class MainWindow(QMainWindow):
    # Initialization Methods
    def __init__(self, ScriptName, AbsoluteDirectoryPath, AppInst):
        # Store Parameters
        self.ScriptName = ScriptName
        self.AbsoluteDirectoryPath = AbsoluteDirectoryPath
        self.AppInst = AppInst

        # Variables
        self.ComparisonInProgress = False
        self.LastSelectedFilePathOne = None
        self.LastSelectedFilePathTwo = None

        # Initialize
        super().__init__()

        # Create Interface
        self.CreateInterface()
        self.show()

        # Center Window
        self.Center()

        # Load Configs
        self.LoadConfigs()

    def CreateInterface(self):
        # Load Theme
        self.LoadTheme()

        # Create Window Icon
        self.WindowIcon = QIcon(self.GetResourcePath("Assets/Comparator Icon.png"))

        # Window Icon and Title
        self.setWindowIcon(self.WindowIcon)
        self.setWindowTitle(self.ScriptName)

        # Button and Line Edit Size Policy
        self.ButtonAndLineEditSizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

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

        self.FileOneProgressLabel = QLabel("File One Progress")
        self.FileOneProgressBar = QProgressBar()
        self.FileTwoProgressLabel = QLabel("File Two Progress")
        self.FileTwoProgressBar = QProgressBar()

        # Widgets to Disable While Comparing
        self.DisableList = []
        self.DisableList.append(self.FolderModeRadioButton)
        self.DisableList.append(self.FileModeRadioButton)
        self.DisableList.append(self.IgnoreNamesInFileModeCheckBox)
        self.DisableList.append(self.AlgorithmComboBox)
        self.DisableList.append(self.FileOneLineEdit)
        self.DisableList.append(self.FileOneSelectButton)
        self.DisableList.append(self.FileTwoLineEdit)
        self.DisableList.append(self.FileTwoSelectButton)
        self.DisableList.append(self.CompareHashesButton)

        # Create Layout
        self.Layout = QGridLayout()

        # Widgets in Layout
        self.Layout.addWidget(self.FolderModeRadioButton, 0, 0, Qt.AlignmentFlag.AlignRight)
        self.Layout.addWidget(self.FileModeRadioButton, 0, 1)
        self.Layout.addWidget(self.IgnoreNamesInFileModeCheckBox, 0, 2)
        self.Layout.addWidget(self.AlgorithmComboBox, 0, 3)
        self.Layout.addWidget(self.FileOneLineEdit, 1, 0, 1, 3)
        self.Layout.addWidget(self.FileOneSelectButton, 1, 3)
        self.Layout.addWidget(self.FileTwoLineEdit, 2, 0, 1, 3)
        self.Layout.addWidget(self.FileTwoSelectButton, 2, 3)
        self.Layout.addWidget(self.CompareHashesButton, 3, 0, 1, 4)
        self.ProgressLayout = QGridLayout()
        self.ProgressLayout.addWidget(self.FileOneProgressLabel, 0, 0)
        self.ProgressLayout.addWidget(self.FileOneProgressBar, 0, 1)
        self.ProgressLayout.addWidget(self.FileTwoProgressLabel, 0, 2)
        self.ProgressLayout.addWidget(self.FileTwoProgressBar, 0, 3)
        self.Layout.addLayout(self.ProgressLayout, 4, 0, 1, 4)

        # Set and Configure Layout
        self.Layout.setColumnStretch(0, 1)
        self.Layout.setColumnStretch(1, 1)
        self.Layout.setColumnStretch(2, 1)
        self.Layout.setRowStretch(3, 1)
        self.Frame.setLayout(self.Layout)

        # Create Actions
        self.CreateActions()

        # Create Menu Bar
        self.CreateMenuBar()

        # Create Status Bar
        self.StatusBar = self.statusBar()

        # Set Central Frame
        self.setCentralWidget(self.Frame)

        # Create Keybindings
        self.CreateKeybindings()

    def CreateActions(self):
        self.SetThemeAction = QAction("Set Theme")
        self.SetThemeAction.triggered.connect(self.SetTheme)

        self.QuitAction = QAction("Quit")
        self.QuitAction.triggered.connect(self.close)

    def CreateMenuBar(self):
        self.MenuBar = self.menuBar()

        self.FileMenu = self.MenuBar.addMenu("File")
        self.FileMenu.addAction(self.SetThemeAction)
        self.FileMenu.addSeparator()
        self.FileMenu.addAction(self.QuitAction)

    def CreateKeybindings(self):
        self.DefaultKeybindings = {}
        self.DefaultKeybindings["QuitAction"] = "Ctrl+Q"

    def LoadConfigs(self):
        # Folder Mode
        FolderModeFile = self.GetResourcePath("Configs/FolderMode.cfg")
        if os.path.isfile(FolderModeFile):
            with open(FolderModeFile, "r") as FolderModeConfigFile:
                TargetRadioButton = self.FolderModeRadioButton if json.loads(FolderModeConfigFile.read()) else self.FileModeRadioButton
                TargetRadioButton.setChecked(True)

        # Ignore Names
        IgnoreNamesFile = self.GetResourcePath("Configs/IgnoreNames.cfg")
        if os.path.isfile(IgnoreNamesFile):
            with open(IgnoreNamesFile, "r") as IgnoreNamesConfigFile:
                self.IgnoreNamesInFileModeCheckBox.setChecked(json.loads(IgnoreNamesConfigFile.read()))

        # Keybindings
        KeybindingsFile = self.GetResourcePath("Configs/Keybindings.cfg")
        if os.path.isfile(KeybindingsFile):
            with open(KeybindingsFile, "r") as ConfigFile:
                self.Keybindings = json.loads(ConfigFile.read())
        else:
            self.Keybindings = copy.deepcopy(self.DefaultKeybindings)
        for Action, Keybinding in self.DefaultKeybindings.items():
            if Action not in self.Keybindings:
                self.Keybindings[Action] = Keybinding
        InvalidBindings = []
        for Action in self.Keybindings.keys():
            if Action not in self.DefaultKeybindings:
                InvalidBindings.append(Action)
        for InvalidBinding in InvalidBindings:
            del self.Keybindings[InvalidBinding]
        for Action, Keybinding in self.Keybindings.items():
            getattr(self, Action).setShortcut(Keybinding)

    def SaveConfigs(self):
        if not os.path.isdir(self.GetResourcePath("Configs")):
            os.mkdir(self.GetResourcePath("Configs"))

        # Folder Mode
        with open(self.GetResourcePath("Configs/FolderMode.cfg"), "w") as FolderModeConfigFile:
            FolderModeConfigFile.write(json.dumps(self.FolderModeRadioButton.isChecked()))

        # Ignore Names
        with open(self.GetResourcePath("Configs/IgnoreNames.cfg"), "w") as IgnoreNamesConfigFile:
            IgnoreNamesConfigFile.write(json.dumps(self.IgnoreNamesInFileModeCheckBox.isChecked()))

        # Keybindings
        with open(self.GetResourcePath("Configs/Keybindings.cfg"), "w") as ConfigFile:
            ConfigFile.write(json.dumps(self.Keybindings, indent=2))

        # Theme
        with open(self.GetResourcePath("Configs/Theme.cfg"), "w") as ConfigFile:
            ConfigFile.write(json.dumps(self.Theme))

    def GetResourcePath(self, RelativeLocation):
        return os.path.join(self.AbsoluteDirectoryPath, RelativeLocation)

    # Input Methods
    def ClearInput(self):
        self.FileOneLineEdit.clear()
        self.FileTwoLineEdit.clear()
        self.LastSelectedFilePathOne = None
        self.LastSelectedFilePathTwo = None

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
        if FileLineEdit is self.FileOneLineEdit:
            LastSelectedFilePath = self.LastSelectedFilePathOne
        elif FileLineEdit is self.FileTwoLineEdit:
            LastSelectedFilePath = self.LastSelectedFilePathTwo
        if LastSelectedFilePath is not None:
            LastSelectedFilePathDirectory = os.path.dirname(LastSelectedFilePath)
            if os.path.exists(LastSelectedFilePathDirectory):
                CurrentPath = LastSelectedFilePathDirectory
        if self.FolderModeRadioButton.isChecked():
            Selected = QFileDialog.getExistingDirectory(caption="Select Folder", directory=CurrentPath)
        else:
            Selected = QFileDialog.getOpenFileName(caption="Select File", directory=CurrentPath)[0]
        if Selected != "":
            FileLineEdit.setText(Selected)
            if FileLineEdit is self.FileOneLineEdit:
                self.LastSelectedFilePathOne = Selected
            elif FileLineEdit is self.FileTwoLineEdit:
                self.LastSelectedFilePathTwo = Selected

    # Hashing Methods
    def CompareHashes(self):
        FileOne = self.FileOneLineEdit.text()
        FileTwo = self.FileTwoLineEdit.text()

        # Validate Inputs
        if FileOne == "" or FileTwo == "":
            self.DisplayMessageBox("Two files must be selected to compare.")
            return
        if not (os.path.exists(FileOne) and os.path.exists(FileTwo)):
            self.DisplayMessageBox("At least one file does not exist.", Icon=QMessageBox.Icon.Warning)
            return
        if FileOne == FileTwo:
            self.DisplayMessageBox("Must select different files to compare.")
            return

        # Check Whether to Ignore File Names
        if self.FileModeRadioButton.isChecked() and self.IgnoreNamesInFileModeCheckBox.isChecked():
            IgnoreNames = True
        else:
            IgnoreNames = False

        # Compare
        self.SetComparisonInProgress(True)
        ComparisonThreadInst = ComparisonThread(FileOne, FileTwo, Algorithm=self.AlgorithmComboBox.currentText(), IgnoreSingleFileNames=IgnoreNames)
        ComparisonThreadInst.ComparisonDoneSignal.connect(lambda: self.DisplayResult(ComparisonThreadInst))
        ComparisonThreadInst.start()

        # Set Up Status Checking
        while threading.active_count() < 4 and not ComparisonThreadInst.ComparisonDone:
            pass
        try:
            HashThreadOne = [RunningThread for RunningThread in threading.enumerate() if RunningThread.name == "HashThreadOne"][0]
            HashThreadTwo = [RunningThread for RunningThread in threading.enumerate() if RunningThread.name == "HashThreadTwo"][0]
        except IndexError:
            HashThreadOne = None
            HashThreadTwo = None
        if HashThreadOne is not None and HashThreadTwo is not None:
            StatusThreadInst = StatusThread(HashThreadOne, HashThreadTwo)
            StatusThreadInst.UpdateProgressSignal.connect(lambda: self.UpdateProgress(HashThreadOne, HashThreadTwo))
            StatusThreadInst.start()

    def DisplayResult(self, ComparisonThread):
        # Clear In-Progress
        self.SetComparisonInProgress(False)

        # Get Result
        FilesIdentical = ComparisonThread.Result

        # Display Result
        if FilesIdentical is None:
            self.DisplayMessageBox("An error occurred.  Files were not compared.", Icon=QMessageBox.Icon.Warning)
        elif FilesIdentical:
            self.DisplayMessageBox("Files are identical!")
        else:
            self.DisplayMessageBox("Files are not identical!", Icon=QMessageBox.Icon.Warning)

    # Interface Methods
    def DisplayMessageBox(self, Message, Icon=QMessageBox.Icon.Information, Buttons=QMessageBox.StandardButton.Ok, Parent=None):
        MessageBox = QMessageBox(self if Parent is None else Parent)
        MessageBox.setWindowIcon(self.WindowIcon)
        MessageBox.setWindowTitle(self.ScriptName)
        MessageBox.setIcon(Icon)
        MessageBox.setText(Message)
        MessageBox.setStandardButtons(Buttons)
        return MessageBox.exec()

    def SetComparisonInProgress(self, ComparisonInProgress):
        self.ComparisonInProgress = ComparisonInProgress
        for Widget in self.DisableList:
            Widget.setDisabled(ComparisonInProgress)
        if ComparisonInProgress:
            self.StatusBar.showMessage("Comparison in progress...")
        else:
            self.StatusBar.clearMessage()
            self.FileOneProgressBar.reset()
            self.FileTwoProgressBar.reset()

    def UpdateProgress(self, HashThreadOne, HashThreadTwo):
        if HashThreadOne.InputSize <= 0 or HashThreadTwo.InputSize <= 0:
            return
        HashThreadOneProgress = floor((HashThreadOne.HashedBytes / HashThreadOne.InputSize) * 100)
        HashThreadTwoProgress = floor((HashThreadTwo.HashedBytes / HashThreadTwo.InputSize) * 100)
        self.FileOneProgressBar.setValue(HashThreadOneProgress)
        self.FileTwoProgressBar.setValue(HashThreadTwoProgress)

    # Window Management Methods
    def Center(self):
        FrameGeometryRectangle = self.frameGeometry()
        DesktopCenterPoint = QApplication.primaryScreen().availableGeometry().center()
        FrameGeometryRectangle.moveCenter(DesktopCenterPoint)
        self.move(FrameGeometryRectangle.topLeft())

    def CreateThemes(self):
        self.Themes = {}

        # Light
        self.Themes["Light"] = QPalette()
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, QColor(240, 240, 240, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(120, 120, 120, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, QColor(240, 240, 240, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.AlternateBase, QColor(247, 247, 247, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipBase, QColor(255, 255, 220, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipText, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.PlaceholderText, QColor(0, 0, 0, 128))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(120, 120, 120, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, QColor(240, 240, 240, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(120, 120, 120, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.BrightText, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Light, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Midlight, QColor(247, 247, 247, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Dark, QColor(160, 160, 160, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Mid, QColor(160, 160, 160, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Shadow, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight, QColor(0, 120, 215, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Link, QColor(0, 0, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.LinkVisited, QColor(255, 0, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, QColor(240, 240, 240, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.AlternateBase, QColor(233, 231, 227, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipBase, QColor(255, 255, 220, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipText, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.PlaceholderText, QColor(0, 0, 0, 128))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, QColor(240, 240, 240, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.BrightText, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Light, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Midlight, QColor(227, 227, 227, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Dark, QColor(160, 160, 160, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Mid, QColor(160, 160, 160, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Shadow, QColor(105, 105, 105, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Highlight, QColor(0, 120, 215, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.HighlightedText, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Link, QColor(0, 0, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.LinkVisited, QColor(255, 0, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, QColor(240, 240, 240, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.AlternateBase, QColor(233, 231, 227, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipBase, QColor(255, 255, 220, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipText, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.PlaceholderText, QColor(0, 0, 0, 128))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, QColor(240, 240, 240, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.BrightText, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Light, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Midlight, QColor(227, 227, 227, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Dark, QColor(160, 160, 160, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Mid, QColor(160, 160, 160, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Shadow, QColor(105, 105, 105, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Highlight, QColor(240, 240, 240, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.HighlightedText, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Link, QColor(0, 0, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.LinkVisited, QColor(255, 0, 255, 255))

        # Dark
        self.Themes["Dark"] = QPalette()
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(98, 108, 118, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.AlternateBase, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipBase, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipText, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.PlaceholderText, QColor(239, 240, 241, 128))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(98, 108, 118, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(98, 108, 118, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.BrightText, QColor(255, 255, 255, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Light, QColor(24, 27, 29, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Midlight, QColor(36, 40, 44, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Dark, QColor(98, 108, 118, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Mid, QColor(65, 72, 78, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Shadow, QColor(0, 0, 0, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight, QColor(65, 72, 78, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText, QColor(36, 40, 44, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Link, QColor(41, 128, 185, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.LinkVisited, QColor(127, 140, 141, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, QColor(35, 38, 41, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.AlternateBase, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipBase, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipText, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.PlaceholderText, QColor(239, 240, 241, 128))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.BrightText, QColor(255, 255, 255, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Light, QColor(24, 27, 29, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Midlight, QColor(36, 40, 44, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Dark, QColor(98, 108, 118, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Mid, QColor(65, 72, 78, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Shadow, QColor(0, 0, 0, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Highlight, QColor(61, 174, 233, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.HighlightedText, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Link, QColor(41, 128, 185, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.LinkVisited, QColor(127, 140, 141, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, QColor(35, 38, 41, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.AlternateBase, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipBase, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipText, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.PlaceholderText, QColor(239, 240, 241, 128))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.BrightText, QColor(255, 255, 255, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Light, QColor(24, 27, 29, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Midlight, QColor(36, 40, 44, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Dark, QColor(98, 108, 118, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Mid, QColor(65, 72, 78, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Shadow, QColor(0, 0, 0, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Highlight, QColor(61, 174, 233, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.HighlightedText, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Link, QColor(41, 128, 185, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.LinkVisited, QColor(127, 140, 141, 255))

    def LoadTheme(self):
        self.CreateThemes()
        ThemeFile = self.GetResourcePath("Configs/Theme.cfg")
        if os.path.isfile(ThemeFile):
            with open(ThemeFile, "r") as ConfigFile:
                self.Theme = json.loads(ConfigFile.read())
        else:
            self.Theme = "Light"
        self.AppInst.setStyle("Fusion")
        self.AppInst.setPalette(self.Themes[self.Theme])

    def SetTheme(self):
        Themes = list(self.Themes.keys())
        Themes.sort()
        CurrentThemeIndex = Themes.index(self.Theme)
        Theme, OK = QInputDialog.getItem(self, "Set Theme", "Set theme (requires restart to take effect):", Themes, current=CurrentThemeIndex, editable=False)
        if OK:
            self.Theme = Theme
            self.DisplayMessageBox(f"The new theme will be active after {self.ScriptName} is restarted.")

    # Close Event
    def closeEvent(self, event):
        if self.ComparisonInProgress:
            if self.DisplayMessageBox("A comparison is in progress.  Exit anyway?", Icon=QMessageBox.Icon.Question, Buttons=(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)) == QMessageBox.StandardButton.Yes:
                self.SaveConfigs()
                event.accept()
            else:
                event.ignore()
        else:
            self.SaveConfigs()
            event.accept()
