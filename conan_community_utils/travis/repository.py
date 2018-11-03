
class Repository(object):

    def __init__(self, travis_repository, travis):
        self._travis = travis
        self._travis_repository = travis_repository

    def __str__(self):
        return self.slug

    @property
    def slug(self):
        return self._travis_repository.slug

