
from conan_community_utils.utils.lazy_property import lazy_property
from .version import PackageVersion


class Package(object):

    def __init__(self, parent, name):
        self._parent = parent
        self._name = name

    def __call__(self, *url):
        return self._parent('packages', self._name, *url)

    def __getattr__(self, item):
        """ Fallback to bintray.Package properties if not overriden """
        return self.data.get(item)

    def __str__(self):
        return self._name

    @lazy_property
    def data(self):
        return self.__call__()

    def get_versions(self):
        for version in self.versions:
            yield PackageVersion(repository=self, name=version)
