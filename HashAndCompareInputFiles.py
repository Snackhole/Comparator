import hashlib
import json
import os


def HashAndCompareInputFiles(InputOne, InputTwo, Algorithm=None):
    # Validate Inputs
    if not os.path.exists(InputOne) and os.path.exists(InputTwo):
        print("At least one input does not exist.")
        return
    if not ((os.path.isdir(InputOne) and os.path.isdir(InputTwo)) or (os.path.isfile(InputOne) and os.path.isfile(InputTwo))):
        print("Inputs must both be files or both be directories.")
        return

    # Determine Algorithm
    AvailableAlgorithms = sorted(list(hashlib.algorithms_available))
    DefaultAlgorithm = "sha256"
    if Algorithm is None:
        Algorithm = DefaultAlgorithm
    if Algorithm not in AvailableAlgorithms:
        print("Algorithm not available.")
        return

    # Hash Inputs
    def HashInput(Input):
        AbsoluteInputPath = os.path.abspath(Input)
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
                HashObject.update(OpenedFile.read())

        # Hash File Paths
        HashObject.update(bytes(json.dumps(FilePaths), "utf-8"))

        # Return Digest of Hash
        return HashObject.digest()

    # TODO:  Threading
    InputOneDigest = HashInput(InputOne)
    InputTwoDigest = HashInput(InputTwo)

    return InputOneDigest == InputTwoDigest
