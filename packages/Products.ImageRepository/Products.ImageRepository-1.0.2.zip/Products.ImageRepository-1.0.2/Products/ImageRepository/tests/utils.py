from os.path import join
from Globals import package_home


PACKAGE_HOME = package_home(globals())

def loadImage(name, size=0):
    """Load image from testing directory
    """
    path = join(PACKAGE_HOME, 'input', name)
    fd = open(path, 'rb')
    data = fd.read()
    fd.close()
    return data

