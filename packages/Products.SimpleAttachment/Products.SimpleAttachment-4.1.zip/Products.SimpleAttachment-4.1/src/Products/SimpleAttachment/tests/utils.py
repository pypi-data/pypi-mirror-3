from os.path import dirname, join


def getFile(filename):
    """ return a file object from the test folder """
    from Products.SimpleAttachment import tests
    filename = join(dirname(tests.__file__), filename)
    return open(filename, 'r')


def getData(filename):
    """ return file data """
    return getFile(filename).read()
