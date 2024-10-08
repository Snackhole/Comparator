import hashlib
import json
import os
import queue
import threading
from math import ceil


def HashAndCompareInputFiles(InputOne, InputTwo, Algorithm=None, IgnoreSingleFileNames=True):
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

    # Check for Identical File Names When Not Ignoring File Names
    if os.path.isfile(InputOne) and os.path.isfile(InputTwo) and not IgnoreSingleFileNames:
        if os.path.basename(InputOne) != os.path.basename(InputTwo):
            return False

    # Check File Sizes
    def GetFileSize(Input):
        if os.path.isfile(Input):
            return os.path.getsize(Input)
        elif os.path.isdir(Input):
            CurrentTotal = 0
            for File in os.listdir(Input):
                CurrentTotal += GetFileSize(os.path.join(Input, File))
            return CurrentTotal
        else:
            return None

    InputOneSize = GetFileSize(InputOne)
    InputTwoSize = GetFileSize(InputTwo)

    if InputOneSize is None or InputTwoSize is None:
        print("An error occurred determining file size.  Comparison not completed.")
        return None

    if InputOneSize != InputTwoSize:
        return False

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
            print(f"No default algorithm is present.  Available algorithms:\n\n{str(AvailableAlgorithms)}")
            return None
    if Algorithm not in AvailableAlgorithms:
        print(f"Algorithm not available.  Available algorithms:\n\n{str(AvailableAlgorithms)}")
        return None

    # Hash Inputs
    class HashThread(threading.Thread):
        def __init__(self, Name, Input, InputSize, ResultQueue):
            # Variables
            self.ChunkSize = 65536
            self.HashedBytes = 0
            self.HashComplete = False

            # Store Parameters
            self.Input = Input
            self.InputSize = ceil(InputSize / self.ChunkSize) * self.ChunkSize
            self.ResultQueue = ResultQueue

            # Initialize
            super().__init__(name=Name, daemon=True)

        def run(self):
            InputDirectory = os.path.dirname(self.Input)
            RelativeInputPath = os.path.basename(self.Input)
            FilePaths = []

            def MapFilePaths(InputDirectory, RelativeInputPath, FilePaths):
                CurrentFile = os.path.join(InputDirectory, RelativeInputPath)
                if os.path.isfile(CurrentFile):
                    FilePaths.append(RelativeInputPath)
                elif os.path.isdir(CurrentFile):
                    for File in os.listdir(CurrentFile):
                        MapFilePaths(InputDirectory, os.path.join(RelativeInputPath, File), FilePaths)

            MapFilePaths(InputDirectory, RelativeInputPath, FilePaths)

            FilePaths.sort()

            # Create Hash Object
            HashObject = hashlib.new(Algorithm)

            # Hash Files in File Paths
            for File in [os.path.join(InputDirectory, RelativeFile) for RelativeFile in FilePaths]:
                with open(File, "rb") as OpenedFile:
                    while OpenedFileChunk := OpenedFile.read(self.ChunkSize):
                        HashObject.update(OpenedFileChunk)
                        self.HashedBytes += self.ChunkSize

            # Hash File Paths
            if not IgnoreSingleFileNames:
                HashObject.update(bytes(json.dumps(FilePaths), "utf-8"))

            # Put Hash Digest in Result Queue
            self.ResultQueue.put(HashObject.digest())

            # Flag Hash Complete
            self.HashComplete = True

    # Check Inputs in Threads
    ResultQueue = queue.Queue()
    InputOneThread = HashThread("HashThreadOne", InputOne, InputOneSize, ResultQueue)
    InputOneThread.start()
    InputTwoThread = HashThread("HashThreadTwo", InputTwo, InputTwoSize, ResultQueue)
    InputTwoThread.start()
    InputOneThread.join()
    InputTwoThread.join()
    DigestOne = ResultQueue.get()
    DigestTwo = ResultQueue.get()

    return DigestOne == DigestTwo
