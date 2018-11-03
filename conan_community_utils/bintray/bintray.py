
import os
import requests

from .repository import Repository

BINTRAY_API_URL = 'https://bintray.com/api/v1'


class Bintray(object):

    def __init__(self, api_username, api_token):
        self._username = api_username
        self._auth = requests.auth.HTTPBasicAuth(api_username, api_token)

    def __call__(self, *url):
        url = '/'.join([BINTRAY_API_URL, '/'.join(url)])
        r = requests.get(url, auth=self._auth, verify=True)
        return r.json()

    def get_repositories(self, user):
        data = self('repos', user)
        for item in data:
            yield Repository(bintray=self, username=user, repository=item['name'])


if __name__ == '__main__':
    from pprint import pprint

    user = 'jgsogo'
    token = os.getenv("BINTRAY_TOKEN")

    b = Bintray(api_username=user, api_token=token)
    repos = b.get_repositories('conan')

    for repo in repos:
        print("Repository: '{}'".format(repo))
        if repo.name == 'conan-center':
            print("\tThere are {} packages:".format(repo.package_count))
            for pck in repo.get_packages():
                print("\t- {}".format(pck))
                for version in pck.get_versions():
                    print("\t\t+ {}".format(version))
                    # pprint(version.data)
