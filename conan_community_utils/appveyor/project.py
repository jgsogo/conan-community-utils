
class Project(object):
    def __init__(self, data, appveyor):
        self._appveyor = appveyor
        self._data = data

    def __str__(self):
        return self.name

    def __getattr__(self, item):
        return self._data.get(item)


