
import re
import requests
import logging
from urllib.parse import quote

from .package import Package
from .package_version import PackageVersion


log = logging.getLogger(__name__)
BINTRAY_API_URL = 'https://bintray.com/api/v1'


class Bintray(object):

    subject = 'conan-community'
    repo = 'conan'

    def __init__(self, api_username, api_token):
        self._username = api_username
        self._auth = requests.auth.HTTPBasicAuth(api_username, api_token)

    @classmethod
    def repo_to_library_name(cls, repo_name):
        ret = repo_name
        if '/' in repo_name:
            repo_name = repo_name.rsplit('/')[1]
        if bool(re.match(r"conan-[\w_]+", repo_name, re.IGNORECASE)):
            ret = repo_name.split('-', 1)[1]
        return ret

    @classmethod
    def branch_to_version(cls, branch, only_if_stable=True):
        assert '/' in branch, branch
        if only_if_stable:
            assert bool(re.match(r"release/[a-zA-Z0-9_][a-zA-Z0-9_+.-]+", branch)) or \
                   bool(re.match(r"stable/[a-zA-Z0-9_][a-zA-Z0-9_+.-]+", branch)), branch
        return branch.split('/', 1)[1]

    def get_package(self, repo_name, user):
        log.debug(f"Bintray::get_package(repo_name='{repo_name}', user='{user}'')")

        library_name = self.repo_to_library_name(repo_name)
        pck_name = ':'.join([library_name, user])
        url = f"{BINTRAY_API_URL}/packages/{self.subject}/{self.repo}/{quote(pck_name, safe='')}"
        r = requests.get(url, auth=self._auth, verify=True)
        if r.status_code != 200:
            # log.error(f"Package {pck_name} not found (url: {url}): {r.content}")
            raise RuntimeError(f"Package {pck_name} not found (url: {url}): {r.content}")
        r = r.json()
        log.debug(f" - {r}")

        return Package(json_data=r, subject=self.subject, repo=self.repo)

    def get_package_version(self, repo_name, user, branch, only_if_stable=True):
        log.debug(f"Bintray::get_package_version(repo_name='{repo_name}', user='{user}', branch='{branch}')")

        library_name = self.repo_to_library_name(repo_name)
        pck_name = ':'.join([library_name, user])
        version = self.branch_to_version(branch, only_if_stable=only_if_stable)
        channel = 'stable'  # If nothing raises, it is stable
        version_str = ':'.join([version, channel])

        url = f"{BINTRAY_API_URL}/packages/{self.subject}/{self.repo}/{quote(pck_name, safe='')}/versions/{quote(version_str, safe='')}"
        r = requests.get(url, auth=self._auth, verify=True)
        if r.status_code != 200:
            # log.error(f"Package {pck_name} (version='{version_str}') not found (url: {url}): {r.content}")
            raise RuntimeError(f"Package {pck_name} (version='{version_str}') not found (url: {url}): {r.content}")
        r = r.json()
        log.debug(f" - {r}")

        return PackageVersion(json_data=r, subject=self.subject, repo=self.repo)


if __name__ == '__main__':
    import os
    import argparse

    parser = argparse.ArgumentParser(description='Run storages/bintray example')
    parser.add_argument('--repo', help='Repo name')
    parser.add_argument('--user', help='Bintray user')
    parser.add_argument('--branch', action='append', help='Branches to work over')
    parser.add_argument("-v", "--verbose", dest="verbose_count",
                        action="count", default=0,
                        help="increases log verbosity for each occurence.")
    args = parser.parse_args()

    repo = args.repo or 'conan-community/conan-zlib'
    branches = args.branch or ['release/1.2.11', 'testing/1.2.11', 'release/1.2.8']
    user = args.user or 'conan'
    log_level = max(3 - args.verbose_count, 0) * 10

    # Configure login
    logging.basicConfig(level=log_level)
    logging.getLogger('urllib3').setLevel(level=logging.ERROR)
    logging.getLogger('github').setLevel(level=logging.ERROR)

    BINTRAY_TOKEN = os.getenv("BINTRAY_TOKEN")
    BINTRAY_USER = os.getenv("BINTRAY_USER")
    b = Bintray(api_username=BINTRAY_USER, api_token=BINTRAY_TOKEN)

    p = b.get_package(repo_name=repo, user=user)
    print(f"Bintray repo: {p}")
    print(f" - description: {p.url}")
    print(f" - description: {p.description}")
    print(f" - topics: {p.topics}")
    print(f" - license: {p.license}")
    print(f" - homepage: {p.homepage}")
    print(f" - repo_name: {p.repo_name}")
    print(f" - linked_to_conan_center: {p.linked_to_conan_center}")
    print(f" - get_versions: {p.get_versions()}")
    print(f" - repo_url: {p.repo_url}")

    for br in branches:
        pv = b.get_package_version(repo_name=repo, user=user, branch=br, only_if_stable=False)
        print(f" - branch: {br}")
        print(f"\tid: {pv}")
        print(f"\tid: {pv.url}")
        print(f"\tdescription: {pv.description}")
        print(f"\ttopics: {pv.topics}")
