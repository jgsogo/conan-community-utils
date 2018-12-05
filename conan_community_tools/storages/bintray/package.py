
import logging
from urllib.parse import quote

log = logging.getLogger(__name__)


class Package(object):

    def __init__(self, json_data, subject, repo):
        self._json_data = json_data
        self.subject = subject
        self.repo = repo

    def __str__(self):
        return self.name

    @property
    def name(self):
        return self._json_data['name']

    @property
    def url(self):
        return f"https://bintray.com/{self.subject}/{self.repo}/{quote(self.name, safe='')}"

    # Data related to Conan package
    @property
    def description(self):
        return self._json_data['desc']

    @property
    def topics(self):
        return sorted(self._json_data['labels'])

    @property
    def license(self):
        licenses = self._json_data['licenses']
        if len(licenses) != 1:
            log.debug(f"Expected one license, got '{licenses}' for package '{self}'.")
        return ', '.join(licenses)

    @property
    def homepage(self):
        return self._json_data['website_url']

    @property
    def repo_name(self):
        return self._json_data['github_repo']

    @property
    def linked_to_conan_center(self):
        return 'conan-center' in self._json_data['linked_to_repos']

    def get_versions(self):
        return self._json_data['versions']

    @property
    def repo_url(self):
        return self._json_data['vcs_url']
