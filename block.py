from enum import Enum


class BType(Enum):
    UNKNOWN = 0
    OPEN_CREDS = 1
    RECAP = 2
    CONTENT = 3
    CLOSE_CREDS = 4

    @staticmethod
    def get_avail():
        return str(e for e in BType)


class Block:

    def __init__(self, begin=0, end=0):
        self.begin = begin
        self.end = end
        self.type_data = list()

    def add_type(self, b_type=BType.UNKNOWN, start_weight=0):
        block_type = BlockType(b_type, start_weight)
        self.type_data.append(block_type)

    def increment_type(self, b_type, incr=1):
        ind = self.type_data.index(b_type)
        if int != -1:
            self.type_data[ind].increment(incr)
        else:
            self.add_type(b_type, incr)


class BlockType:

    def __init__(self, b_type=BType.UNKNOWN, start_weight=0):
        if isinstance(b_type, BType):
            self.b_type = b_type
        else:
            raise Exception('Unknown block type. Available: {}'.format(BType.get_avail()))
        self.weight = start_weight

    def increment(self, incr=1):
        self.weight += incr



