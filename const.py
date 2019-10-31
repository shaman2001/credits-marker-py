class MetaConstType(type):
    def __getattr__(cls, key):
        return cls[key]

    def __setattr__(cls, key, value):
        raise TypeError


class MetaConst(object, metaclass=MetaConstType):
    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        raise TypeError


class Const(MetaConst):
    INPUT_DIR = 'input/'
    FPS = 25  # frame frequency, frames per second
    SEEK_FACTOR = 6  # range (back & forward) in fractions of the total length to seek the matched frame
    MISMATCH_LIMIT = 5  # mismatched frames in a row limit to stop show the difference
    PART_MATCH_LIMIT = 25  # mismatched frames in a row limit to stop consider as almost matched
    PART_MATCH_RANGE = range(5, 9)  # matched symbols
    BLOCK_PASS_CRITERION = 30  # %
    MIN_BLOCK_DUR = 5  # minimal duration of one block to recognize, sec
