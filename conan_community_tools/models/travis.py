
import dateutil.parser
import requests
import yaml
from urllib.parse import urlencode, quote

import logging
log = logging.getLogger(__name__)

TRAVIS_URL = 'https://api.travis-ci.org'


class Travis(object):
    """ Access travis using v3 """

    def __init__(self, token):
        self._token = token
        self._travis_url = TRAVIS_URL

    def headers(self):
        return {'Travis-API-Version': '3',
                'Authorization': f'token {self._token}'}

    def get_last_build(self, repo, branch, limit=1):
        log.debug(f"Travis::get_last_build(repo={repo}, branch={branch}, limit={limit})")
        url = f'{self._travis_url}/repo/{quote(repo, safe="")}/builds'
        qs = {'branch.name': branch, 'limit': limit,
              'include': 'job.state'}
        r = requests.get(url=url, headers=self.headers(), params=urlencode(qs))
        r = r.json()
        build = r["builds"][0]
        _, build_id = build['@href'].rsplit('/', 1)
        ret = {'url': 'https://travis-ci.org/' + build['repository']['slug'] + '/builds/' + build_id,
               'state': build["state"],
               'jobs': [it["state"] for it in build["jobs"]],
               'commit': {'sha': build["commit"]["sha"],
                          'message': build["commit"]["message"],
                          'committed_at': dateutil.parser.parse(build["commit"]["committed_at"])}
               }
        return ret

    def get_status(self, repo, branch):
        log.debug(f"Travis::get_status(repo='{repo}', branch='{branch}')")
        url = f'{self._travis_url}/repo/{quote(repo, safe="")}'
        r = requests.get(url=url, headers=self.headers())
        from pprint import pprint
        pprint(r.json())


def parse_travis_yml(travis_file):
    log.debug(f"parse_travis_yml(travis_file='{travis_file}')")
    with open(travis_file, 'r') as f:
        data = yaml.load(f.read())

        env_global = data['env']['global']
        if isinstance(env_global, list):
            joined_env_global = {}
            for it in env_global:
                joined_env_global.update(it)
            env_global = joined_env_global

        jobs = data['jobs']['include']  # TODO: Could be matrix/include
        for j in jobs:
            if 'script' in j:
                continue

            job_env = env_global.copy()
            for it in j['env'].split(' '):
                k, v = it.split('=')
                job_env[k] = v
            #print(job_env)
            print(job_env["os"])


if __name__ == '__main__':
    def rate_limits():
        from github import Github

        g = Github(os.getenv("GITHUB_TOKEN"))

        print("Rate limits")
        print(f"Calls: {g.rate_limiting}")
        from datetime import datetime
        print(f"Reset rate: {datetime.fromtimestamp(g.rate_limiting_resettime)}")

    import os

    TRAVIS_TOKEN = os.getenv("TRAVIS_TOKEN")

    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('urllib3').setLevel(level=logging.ERROR)
    logging.getLogger('github').setLevel(level=logging.ERROR)

    yaml_file = r"/Users/jgsogo/dev/conan-packages/tgbot-cpp/.travis.yml"
    r = parse_travis_yml(yaml_file)
    exit(0)

    repo = 'conan-community/conan-zlib'
    branches = ['release/1.2.11', 'testing/1.2.11', 'release/1.2.8']

    rate_limits()

    t = Travis(TRAVIS_TOKEN)
    for branch in branches:
        r = t.get_last_build(repo=repo, branch=branch)
        print(f' - {branch}: {r["state"]}')

    rate_limits()