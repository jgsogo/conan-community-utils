
from conan_community_utils.utils.lazy_property import lazy_property


class PackageVersion(object):

    def __init__(self, repository, name):
        self._repository = repository
        self._name = name

    def __call__(self, root='versions', *url):
        return self._repository(root, self._name, *url)

    def __getattr__(self, item):
        """ Fallback to bintray.Package properties if not overriden """
        return self.data.get(item)

    def __str__(self):
        return self._name

    @lazy_property
    def data(self):
        return self.__call__()

