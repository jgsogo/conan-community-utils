
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
        log.debug(f"Travis::get_settings(repo={repo})")

        url = f'{self._url}/repo/{quote(repo, safe="")}/env_vars'
        r = requests.get(url=url, headers=self.headers())
        r = r.json()
        log.debug(f"{pformat(r)}")

        for it in r["env_vars"]:
            yield it['name'], it.get('value', None), it['public']

    def set_settings(self, values):
        raise NotImplementedError("Travis::set_settings")


if __name__ == '__main__':
    import os
    import argparse

    parser = argparse.ArgumentParser(description='Run Travis example')
    parser.add_argument('--repo', help='Repo name')
    parser.add_argument('--branch', action='append', help='Branches to work over')
    parser.add_argument("-v", "--verbose", dest="verbose_count",
                        action="count", default=0,
                        help="increases log verbosity for each occurence.")
    args = parser.parse_args()

    repo = args.repo or 'conan-community/conan-zlib'
    branches = args.branch or ['release/1.2.11', 'testing/1.2.11', 'release/1.2.8']
    log_level = max(3 - args.verbose_count, 0) * 10

    # Configure login
    logging.basicConfig(level=log_level)
    logging.getLogger('urllib3').setLevel(level=logging.ERROR)
    logging.getLogger('github').setLevel(level=logging.ERROR)

    TRAVIS_TOKEN = os.getenv("TRAVIS_TOKEN")
    t = Travis(TRAVIS_TOKEN)
    print(f"Repo '{repo}'")

    print(f" - env vars:")
    for name, value, public in t.get_settings(repo=repo):
        print(f"\t{name}: {value} {'' if public else '[private]'}")

    for branch in branches:
        r = t.get_last_build(repo=repo, branch=branch)
        print(f' - {branch}: {r}')
        print(f'\tstatus: {r.status}')
        print(f'\tdate: {r.commit["date"]}')
        print(f'\tmessage: {r.commit["message"].splitlines()[0]}')
