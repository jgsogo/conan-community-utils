
class Repository(object):

    def __init__(self, travis_repository, travis):
        self._travis = travis
        self._travis_repository = travis_repository

    def __str__(self):
        return self.full_name

    @property
    def id(self):
        return self.full_name

    @property
    def full_name(self):
        return self._travis_repository["slug"]

    @property
    def travis_url(self):
        try:
            return self._travis_repository["url"]
        except:
            return "no-travis-url"
