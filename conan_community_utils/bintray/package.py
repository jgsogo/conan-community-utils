
from ..utils.lazy_property import lazy_property


class Package(object):

    def __init__(self, parent, name):
        self._parent = parent
        self._name = name

    def __call__(self, root='packages', *url):
        name, _ = self._name.split(':')
        return self._parent(root, self._name, *url)

    def __getattr__(self, item):
        """ Fallback to bintray.Package properties if not overriden """
        return self.data.get(item)

    def __str__(self):
        return self._name

    @lazy_property
    def data(self):
        return self.__call__()
