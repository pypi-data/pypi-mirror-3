"""Get ready for some VooDoo Magic."""

def _isAlias(method):
    return isinstance(method, also)

class AlsoMetaClass(type):
    def __new__(meta, classname, bases, classDict):
        for method in filter(_isAlias, classDict.values()):
            aliases = set()
            while isinstance(method, also):
                aliases.add(method)
                method = method.follower
            else:
                original_method = method

            classDict[original_method.func_name] = original_method
            for alias in aliases:
                classDict[alias.name] = original_method

        return type.__new__(meta, classname, bases, classDict)

class also:
    def __init__(self, name):
        self.name = name

    def __call__(self, method):
        self.follower = method
        return self
