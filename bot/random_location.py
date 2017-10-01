class RandomLocation(object):
    """A Random location in the world, with a name, rate of discovery, and path to an image"""

    def __init__(self, name, rate, img_path, index):
        self.name = name
        self.rate = float(rate)
        self.img_path = img_path
        self.index = index

    def __str__(self):
        return "{0}: rate={1}".format(self.name, self.rate)

    def __repr__(self):
        return "{0}:{1}:{2}:{3}".format(self.name, self.rate, self.img_path, self.index)
