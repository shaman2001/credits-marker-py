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
    input_dir = 'input/'
    fps = 25

