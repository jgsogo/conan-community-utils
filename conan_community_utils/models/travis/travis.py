
from travispy import TravisPy

from .account import Account
from .repository import Repository


class Travis(object):
    def __init__(self, github_token):
        self._travis = TravisPy.github_auth(github_token)

    def __str__(self):
        return self.username

    @property
    def username(self):
        return self._travis.user().login

    def get_accounts(self):
        for it in self._travis.accounts(all=True):
            yield Account(it, self._travis)

    def get_repository(self, full_name):
        return Repository(self._travis.repo(full_name), self._travis)


if __name__ == "__main__":
    import os
    t = Travis(os.getenv("GITHUB_TOKEN"))
    print("User logged in: {}".format(t))

    for account in t.get_accounts():
        print(account)
        for repo in account.get_repositories():
            print("\t- {}".format(repo))

    repo = t.get_repository('conan-community/conan-nasm-installer')
    print(repo)
