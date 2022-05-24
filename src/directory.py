import os
import shutil


def makeDir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def deleteDir(path):
    if os.path.exists(path):
        shutil.rmtree(path)


if __name__ == "__main__":
    print("test well")