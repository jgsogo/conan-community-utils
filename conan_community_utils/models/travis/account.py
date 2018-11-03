
from .repository import Repository


class Account(object):

    def __init__(self, travis_account, travis):
        self._travis = travis
        self._travis_account = travis_account

    def __str__(self):
        return self.id  # ID in Github

    @property
    def id(self):
        return self._travis_account.login  # ID in Github

    def get_repositories(self, active=True):
        for it in self._travis.repos(owner_name=self.id, active=active):
            yield Repository(it, self._travis)

