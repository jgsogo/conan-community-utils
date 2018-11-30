
import requests
from urllib.parse import quote

BINTRAY_API_URL = 'https://bintray.com/api/v1'


class Package(object):
    def __init__(self, json, version, channel):
        self._json = json
        self.name, self.user = self._json['name'].split(':')
        self.version = version
        self.channel = channel

    @property
    def url(self):
        pck_name = ':'.join([self.name, self.user])
        version_str = ':'.join([self.version, self.channel])
        url = f"https://bintray.com/conan-community/conan/{quote(pck_name, safe='')}/{version_str}"
        return url


class Bintray(object):

    def __init__(self, api_username, api_token):
        self._username = api_username
        self._auth = requests.auth.HTTPBasicAuth(api_username, api_token)

    def get_repository(self, name, user):
        pck_name = ':'.join([name, user])
        url = f"{BINTRAY_API_URL}/packages/conan-community/conan/{quote(pck_name, safe='')}"
        r = requests.get(url, auth=self._auth, verify=True)
        if r.status_code != 200:
            raise RuntimeError(f"Repository {pck_name} not found (url: {url}): {r.content}")
        r = r.json()
        return r

    def get_package(self, name, version, user, channel):
        pck_name = ':'.join([name, user])
        url = f"{BINTRAY_API_URL}/packages/conan-community/conan/{quote(pck_name, safe='')}"
        r = requests.get(url, auth=self._auth, verify=True)
        r = r.json()

        version_str = ':'.join([version, channel])
        if version_str not in r['versions']:
            raise RuntimeError(f"Version '{version}' not found")

        return Package(json=r, version=version, channel=channel)


if __name__ == '__main__':
    import os
    from pprint import pprint

    user = 'jgsogo'
    token = os.getenv("BINTRAY_TOKEN")

    b = Bintray(api_username=user, api_token=token)
    jj = b.get_package(name="zlib", version="1.2.9", user="conan", channel="stable")
    pprint(jj)
    exit(0)
