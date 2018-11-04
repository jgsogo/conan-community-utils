
from travispy import TravisPy

from .account import Account
from .repository import Repository


class Travis(object):
    RepositoryClass = Repository

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
        return self.RepositoryClass(travis_repository=self._travis.repo(full_name),
                                    travis=self._travis)


def rate_limits():
    from github import Github

    g = Github(os.getenv("GITHUB_TOKEN"))

    print("Rate limits")
    print("Calls: {}".format(g.rate_limiting))
    from datetime import datetime
    print("Reset rate: {}".format(datetime.fromtimestamp(g.rate_limiting_resettime)))


if __name__ == "__main__":
    import os

    rate_limits()

    t = Travis(os.getenv("GITHUB_TOKEN"))
    print("User logged in: {}".format(t))

    for account in t.get_accounts():
        print(account)
        for repo in account.get_repositories():
            print("\t- {}".format(repo))
            break

    repo = t.get_repository('conan-community/conan-nasm-installer')
    print(repo)

    rate_limits()