

from conan_community_utils.utils.lazy_property import lazy_property
from .package import Package


class Repository(object):

    def __init__(self, bintray, username, repository):
        self._bintray = bintray
        self._username = username
        self._repository = repository

    def __call__(self, root='repos', *url_path):
        return self._bintray(root, self._username, self._repository, *url_path)

    def __getattr__(self, item):
        """ Fallback to bintray.Package properties if not overriden """
        return self.data.get(item)

    def __str__(self):
        return "{}/{}".format(self._username, self._repository)

    @lazy_property
    def data(self):
        return self.__call__()

    def get_packages(self):
        data = self.__call__('repos', 'packages')
        for item in data:
            yield Package(parent=self, name=item['name'])


if __name__ == '__main__':
    repo = Repository('conan', 'conan-center')
    packages = repo.get_packages()
    for it in packages[:3]:
        print(it.name)
