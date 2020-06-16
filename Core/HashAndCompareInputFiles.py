import hashlib
import json
import os
import queue
import threading

# Hashing Thread
class HashingThread(threading.Thread):
    def __init__(self, target, args):
        super().__init__(target=target, args=args)
        self.Stop = False

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

    # Hash Input Function
    def HashInput(Input, ResultQueue):
        # Set Up Thread Stop Flag
        CurrentThread = threading.current_thread()
        assert (isinstance(CurrentThread, HashingThread))

        AbsoluteInputPath = os.path.abspath(Input)
        AbsoluteInputDirectory = os.path.dirname(AbsoluteInputPath)
        RelativeInputPath = os.path.basename(AbsoluteInputPath)
        FilePaths = []

        def MapFilePaths(AbsoluteInputDirectory, RelativeInputPath, FilePaths):
            # Check Thread Stop Flag
            CurrentThread = threading.current_thread()
            assert (isinstance(CurrentThread, HashingThread))
            if CurrentThread.Stop:
                return

            # Map File Paths
            CurrentFile = AbsoluteInputDirectory + "/" + RelativeInputPath
            if os.path.isfile(CurrentFile):
                FilePaths.append(RelativeInputPath)
            elif os.path.isdir(CurrentFile):
                for File in os.listdir(CurrentFile):
                    MapFilePaths(AbsoluteInputDirectory, RelativeInputPath + "/" + File, FilePaths)

        MapFilePaths(AbsoluteInputDirectory, RelativeInputPath, FilePaths)

        # Check Thread Stop Flag
        if CurrentThread.Stop:
            return

        FilePaths.sort()

        # Create Hash Object
        HashObject = hashlib.new(Algorithm)

        # Hash Files in File Paths
        for File in [AbsoluteInputDirectory + "/" + RelativeFile for RelativeFile in FilePaths]:
            # Check Thread Stop Flag
            if CurrentThread.Stop:
                return

            # Open File
            with open(File, "rb") as OpenedFile:
                while OpenedFileChunk := OpenedFile.read(1024):
                    # Check Thread Stop Flag
                    if CurrentThread.Stop:
                        return

                    # Update Hash
                    HashObject.update(OpenedFileChunk)

        # Hash File Paths
        if not IgnoreSingleFileNames:
            HashObject.update(bytes(json.dumps(FilePaths), "utf-8"))

        # Put Hash Digest in Result Queue
        ResultQueue.put(HashObject.digest())

    # Check Inputs in Threads
    ResultQueue = queue.Queue()
    InputOneThread = HashingThread(target=HashInput, args=[InputOne, ResultQueue])
    InputOneThread.start()
    InputTwoThread = HashingThread(target=HashInput, args=[InputTwo, ResultQueue])
    InputTwoThread.start()
    InputOneThread.join()
    InputTwoThread.join()
    DigestOne = ResultQueue.get()
    DigestTwo = ResultQueue.get()

    return DigestOne == DigestTwo
