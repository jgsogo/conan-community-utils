
import os
import dateutil.parser
import requests
import yaml
from urllib.parse import urlencode, quote
from pprint import pformat

from ._base import CIBase, LastBuildInfo
from conan_community_tools.environment import APPVEYOR_ACCOUNT, APPVEYOR_TOKEN

import logging
log = logging.getLogger(__name__)

APPVEYOR_URL = 'https://ci.appveyor.com/api'


def get_client():
    token = os.getenv(APPVEYOR_TOKEN)
    account = os.getenv(APPVEYOR_ACCOUNT)
    if not token or not account:
        raise EnvironmentError(f"Provide env variables '{APPVEYOR_TOKEN}' and '{APPVEYOR_ACCOUNT}'")
    return Appveyor(token=token, account=account)


class Appveyor(CIBase):

    def __init__(self, account, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._url = APPVEYOR_URL
        self._account = account # account or os.getenv("APPVEYOR_ACCOUNT")

    def headers(self):
        return {"Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json"}

    def get_users(self):
        log.debug(f"Appveyor::get_users()")
        url = f"{self._url}/users"
        r = requests.get(url=url, headers=self.headers())
        if r.status_code != 200:
            raise ValueError(f"Cannot get user info: {r.content}")
        r = r.json()
        log.debug(f'{pformat(r)}')
        return r

    @classmethod
    def _translate_state(cls, state):
        if state == "success":
            return LastBuildInfo.BuildStatus.SUCCESS
        elif state == "failed":
            return LastBuildInfo.BuildStatus.FAILED
        else:
            log.error(f"Unknown state value: '{state}'")
            return LastBuildInfo.BuildStatus.UNKNOWN

    @classmethod
    def _fix_repo_name(cls, repo):
        if '/' in repo:
            return repo.split("/")[1]

    def _get_last_build(self, repo_full_name, branch, is_error=True, *args, **kwargs):
        log.debug(f"Appveyor::get_last_build(repo={repo_full_name}, branch={branch})")

        repo = self._fix_repo_name(repo_full_name)
        url = f"{self._url}/projects/{quote(self._account, safe='')}/{quote(repo, safe='')}/branch/{quote(branch, safe='')}"
        r = requests.get(url=url, headers=self.headers())
        r = r.json()
        log.debug(f"{pformat(r)}")

        ret = LastBuildInfo()
        try:

            ret.status = self._translate_state(r["build"]["status"])
            ret.url = f"https://ci.appveyor.com/project/{quote(self._account, safe='')}/{quote(repo, safe='')}/builds/{r['build']['buildId']}"
            ret.commit['sha'] = r["build"]["commitId"]
            ret.commit['message'] = r["build"]["message"] or '<empty>'
            ret.commit['date'] = dateutil.parser.parse(r["build"]["committed"])
            # ret.image_url = f"https://ci.appveyor.com/api/projects/status/2135ith6nulo4cwn/branch/{r['build']['branch']}?svg=true"  # FIXME: I don't know how to get that token
            ret.image_url = f"https://ci.appveyor.com/api/projects/status/github/{quote(repo_full_name, safe='')}?branch={r['build']['branch']}&svg=true"

        except Exception as e:
            if is_error:
                log.error(f"Error retrieving information from last build status for repo '{repo}' "
                          f"(branch='{branch}'): {e}. Returned json was:\n{pformat(r)}")
        finally:
            return ret

    def get_settings(self, repo):
        log.debug(f"Appveyor::get_settings(repo={repo})")

        repo = self._fix_repo_name(repo)
        url = f"{self._url}/projects/{quote(self._account, safe='')}/{quote(repo, safe='')}/settings/environment-variables"
        r = requests.get(url=url, headers=self.headers())
        r = r.json()
        log.debug(f"{pformat(r)}")

        for it in r:
            encrypted = it['value']['isEncrypted']
            yield it['name'], it['value']['value'] if not encrypted else "<encrypted>", bool(not encrypted)

    def set_settings(self, values):
        raise NotImplementedError("Appveyor::set_settings")


if __name__ == '__main__':
    import os
    import argparse

    parser = argparse.ArgumentParser(description='Run Appveyor example')
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

    APPVEYOR_TOKEN = os.getenv("APPVEYOR_TOKEN")
    APPVEYOR_ACCOUNT = os.getenv("APPVEYOR_ACCOUNT")
    t = Appveyor(token=APPVEYOR_TOKEN, account=APPVEYOR_ACCOUNT)
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
