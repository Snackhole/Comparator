import hashlib
import json
import os
import queue
import threading


def HashAndCompareInputFiles(InputOne, InputTwo, Algorithm=None, IgnoreSingleFileNames=False):
    # Validate Inputs
    if not (os.path.exists(InputOne) and os.path.exists(InputTwo)):
        print("At least one input does not exist.")
        return None
    if not ((os.path.isdir(InputOne) and os.path.isdir(InputTwo)) or (os.path.isfile(InputOne) and os.path.isfile(InputTwo))):
        print("Inputs must both be files or both be directories.")
        return None
    if (os.path.isdir(InputOne) or os.path.isdir(InputTwo)) and IgnoreSingleFileNames:
        print("File names can only be ignored when comparing single files.")
        return None
    if InputOne == InputTwo:
        print("Must select different inputs to compare.")
        return None

    # Determine Algorithm
    AvailableAlgorithms = sorted(list(hashlib.algorithms_available))
    DefaultAlgorithm = None
    DefaultAlgorithmOptions = ("md5", "sha1")
    for DefaultAlgorithmOption in DefaultAlgorithmOptions:
        if DefaultAlgorithmOption in AvailableAlgorithms:
            DefaultAlgorithm = DefaultAlgorithmOption
            break
    if Algorithm is None:
        if DefaultAlgorithm is not None:
            Algorithm = DefaultAlgorithm
        else:
            print("No default algorithm is present.")
            return None
    if Algorithm not in AvailableAlgorithms:
        print("Algorithm not available.")
        return None

    # Hash Inputs
    class HashThread(threading.Thread):
        def __init__(self, Input, ResultQueue):
            self.Input = Input
            self.ResultQueue = ResultQueue
            super().__init__(daemon=True)

        def run(self):
            AbsoluteInputPath = os.path.abspath(self.Input)
            AbsoluteInputDirectory = os.path.dirname(AbsoluteInputPath)
            RelativeInputPath = os.path.basename(AbsoluteInputPath)
            FilePaths = []

            def MapFilePaths(AbsoluteInputDirectory, RelativeInputPath, FilePaths):
                CurrentFile = AbsoluteInputDirectory + "/" + RelativeInputPath
                if os.path.isfile(CurrentFile):
                    FilePaths.append(RelativeInputPath)
                elif os.path.isdir(CurrentFile):
                    for File in os.listdir(CurrentFile):
                        MapFilePaths(AbsoluteInputDirectory, RelativeInputPath + "/" + File, FilePaths)

            MapFilePaths(AbsoluteInputDirectory, RelativeInputPath, FilePaths)

            FilePaths.sort()

            # Create Hash Object
            HashObject = hashlib.new(Algorithm)

            # Hash Files in File Paths
            for File in [AbsoluteInputDirectory + "/" + RelativeFile for RelativeFile in FilePaths]:
                with open(File, "rb") as OpenedFile:
                    while OpenedFileChunk := OpenedFile.read(65536):
                        HashObject.update(OpenedFileChunk)

            # Hash File Paths
            if not IgnoreSingleFileNames:
                HashObject.update(bytes(json.dumps(FilePaths), "utf-8"))

            # Put Hash Digest in Result Queue
            self.ResultQueue.put(HashObject.digest())

    # Check Inputs in Threads
    ResultQueue = queue.Queue()
    InputOneThread = HashThread(InputOne, ResultQueue)
    InputOneThread.start()
    InputTwoThread = HashThread(InputTwo, ResultQueue)
    InputTwoThread.start()
    InputOneThread.join()
    InputTwoThread.join()
    DigestOne = ResultQueue.get()
    DigestTwo = ResultQueue.get()

    return DigestOne == DigestTwo


class ComparisonThread(threading.Thread):
    def __init__(self, MainWindow, InputOne, InputTwo, Algorithm=None, IgnoreSingleFileNames=False) -> None:
        self.MainWindow = MainWindow
        self.InputOne = InputOne
        self.InputTwo = InputTwo
        self.Algorithm = Algorithm
        self.IgnoreSingleFileNames = IgnoreSingleFileNames
        self.Result = None
        super().__init__()

    def run(self) -> None:
        self.Result = HashAndCompareInputFiles(self.InputOne, self.InputTwo, Algorithm=self.Algorithm, IgnoreSingleFileNames=self.IgnoreSingleFileNames)
        self.MainWindow.DisplayResult(self.Result)
