
import dateutil.parser
import requests
import yaml
from urllib.parse import urlencode, quote
from pprint import pformat

from ._base import CIBase, LastBuildInfo

import logging
log = logging.getLogger(__name__)

TRAVIS_URL = 'https://api.travis-ci.org'


class Travis(CIBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._url = TRAVIS_URL

    def headers(self):
        return {'Travis-API-Version': '3',
                'Authorization': f'token {self._token}'}

    @classmethod
    def _translate_state(cls, state):
        if state == "passed":
            return LastBuildInfo.BuildStatus.SUCCESS
        else:
            log.error(f"Unknown state value: '{state}'")
            return LastBuildInfo.BuildStatus.UNKNOWN

    def _get_last_build(self, repo, branch, *args, **kwargs):
        log.debug(f"Travis::get_last_build(repo={repo}, branch={branch})")

        url = f'{self._url}/repo/{quote(repo, safe="")}/builds'
        qs = {'branch.name': branch, 'limit': 1, 'include': 'job.state'}
        r = requests.get(url=url, headers=self.headers(), params=urlencode(qs))
        r = r.json()
        log.debug(f"{pformat(r)}")

        ret = LastBuildInfo()
        try:
            build = r["builds"][0]
            _, build_id = build['@href'].rsplit('/', 1)

            ret.status = self._translate_state(build["state"])
            ret.url = 'https://travis-ci.org/' + build['repository']['slug'] + '/builds/' + build_id
            ret.commit['sha'] = build["commit"]["sha"]
            ret.commit['message'] = build["commit"]["message"]
            ret.commit['date'] = dateutil.parser.parse(build["commit"]["committed_at"])

        except Exception as e:
            log.error(f"Error retrieving information from last build status for repo '{repo}' "
                      f"(branch='{branch}'): {e}. Returned json was:\n{pformat(r)}")
        finally:
            return ret

    def get_settings(self, repo):
        pass


if __name__ == '__main__':
    import os
    TRAVIS_TOKEN = os.getenv("TRAVIS_TOKEN")

    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('urllib3').setLevel(level=logging.ERROR)
    logging.getLogger('github').setLevel(level=logging.ERROR)

    repo = 'conan-community/conan-zlib'
    branches = ['release/1.2.11', 'testing/1.2.11', 'release/1.2.8']

    t = Travis(TRAVIS_TOKEN)
    for branch in branches:
        r = t.get_last_build(repo=repo, branch=branch)
        print(f' - {branch}: {r}')
        break
