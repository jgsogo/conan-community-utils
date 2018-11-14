
import os
import dateutil.parser
import requests

import logging
log = logging.getLogger(__name__)

APPVEYOR_URL = 'https://ci.appveyor.com/api'


class Appveyor(object):

    def __init__(self, token):
        self._token = token
        self._appveyor_url = APPVEYOR_URL

    def headers(self):
        return {"Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json"}

    def check(self, account, repo):
        url = f"{self._appveyor_url}/projects/{account}/{repo}"
        log.debug(f" - url: {url}")
        log.debug(f" - headers: {self.headers()}")
        r = requests.get(url=url, headers=self.headers())
        r = r.json()
        print(r)

    def get_last_build(self, repo, branch, account=None):
        account = account or os.getenv("APPVEYOR_ACCOUNT")
        log.debug(f"Appveyor::get_last_build(repo='{repo}', branch='{branch}')")
        url = f"{self._appveyor_url}/projects/{quote(account, safe='')}/{quote(repo, safe='')}/branch/{quote(branch, safe='')}"
        r = requests.get(url=url, headers=self.headers())
        r = r.json()

        url = f"https://ci.appveyor.com/project/{quote(account, safe='')}/{quote(repo, safe='')}/builds/{r['build']['buildId']}"
        ret = {'commit': {'sha': r["build"]["commitId"],
                          'datetime': dateutil.parser.parse(r["build"]["committed"],)},
               'jobs': [it["status"] for it in r["build"]["jobs"]],
               'status': r["build"]["status"],
               'url': url}

        return ret


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('urllib3').setLevel(level=logging.ERROR)
    logging.getLogger('github').setLevel(level=logging.ERROR)

    account = 'ConanCIintegration'
    repo = 'conan-zlib'
    branches = ['release/1.2.11', 'testing/1.2.11', ]

    token = os.getenv("APPVEYOR_TOKEN")
    t = Appveyor(token)
    #t.check(account, repo)
    for branch in branches:
        r = t.get_last_build(account=account, repo=repo, branch=branch)
        print(f" - {branch}: {r['status']}")
