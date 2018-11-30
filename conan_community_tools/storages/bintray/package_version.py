
from urllib.parse import quote


class PackageVersion(object):

    def __init__(self, json_data, subject, repo):
        self._json_data = json_data
        self.subject = subject
        self.repo = repo
        self.version, self.channel = self._json_data['name'].split(':')
        self.name, self.username = self._json_data['package'].split(':')

    def __str__(self):
        return f"{self.name}/{self.version}@{self.username}/{self.channel}"

    @property
    def url(self):
        version_str = ':'.join([self.version, self.channel])
        pkg_name = ':'.join([self.name, self.username])
        return f"https://bintray.com/{self.subject}/{self.repo}/{quote(pkg_name, safe='')}/{quote(version_str, safe='')}"

    @property
    def description(self):
        return self._json_data['desc']

    @property
    def topics(self):
        return sorted(self._json_data['labels'])
