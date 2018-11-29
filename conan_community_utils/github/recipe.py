
import os
import re
import functools
from github.Repository import Repository

from .files import ConanFile, Readme, TravisYML, AppveyorYML, BuildPy
from conan_community_utils.ci.travis import Travis
from conan_community_utils.ci.appveyor import Appveyor

"""
from conan_community_utils.models.travis import Travis
from conan_community_utils.models.appveyor import Appveyor
from conan_community_utils.models.bintray import Bintray
"""

import logging
log = logging.getLogger(__name__)


class Recipe(object):
    """ Models a conan recipe in Github """

    travis = Travis(token=os.getenv("TRAVIS_TOKEN"))
    appveyor = Appveyor(token=os.getenv("APPVEYOR_TOKEN"), account=os.getenv("APPVEYOR_ACCOUNT"))
    # bintray = Bintray(api_token=os.getenv("BINTRAY_TOKEN"), api_username=os.getenv("BINTRAY_USERNAME"))

    def __init__(self, repo):
        assert isinstance(repo, Repository)
        self._repo = repo

    def __str__(self):
        return self.id

    @classmethod
    def is_recipe(cls, repo_id):
        return bool(re.match(r"conan-[\w_]+", repo_id, re.IGNORECASE))

    @classmethod
    def is_release_branch(cls, branch):
        return bool(re.match(r"release/[a-zA-Z0-9_][a-zA-Z0-9_+.-]+", branch)) or \
               bool(re.match(r"stable/[a-zA-Z0-9_][a-zA-Z0-9_+.-]+", branch))

    @property
    def id(self):
        return str(self._repo.name)

    @property
    def full_name(self):
        return self._repo.full_name

    @functools.lru_cache()
    def get_branches(self):
        return [branch.name for branch in self._repo.get_branches()]

    # At repo level
    @functools.lru_cache()
    def get_topics(self):
        return self._repo.get_topics()

    @functools.lru_cache()
    def get_license(self):
        try:
            return self._repo.get_license()
        except Exception as e:
            log.error(f"Cannot retrieve license (repo {self.full_name}): ({type(e)}) {e}")
            return None

    @property
    def default_branch(self):
        return self._repo.default_branch

    @property
    def homepage(self):
        return self._repo.homepage

    @property
    def description(self):
        return self._repo.description

    # Branch level calls
    def _get_file(self, branch, FileClass, filepath=''):
        try:
            path = os.path.join(filepath, FileClass.name)
            content = self._repo.get_contents(path, ref=branch).decoded_content.decode("utf-8")
        except Exception as e:
            log.error(f"Cannot retrieve '{path}' (repo {self.full_name}) from "
                      f"branch {branch}): ({type(e)}) {e}")
            return None
        else:
            return FileClass(content=content)

    @functools.lru_cache()
    def get_conanfile_file(self, branch):
        return self._get_file(branch=branch, FileClass=ConanFile)

    @functools.lru_cache()
    def get_readme_file(self, branch):
        return self._get_file(branch=branch, FileClass=Readme)

    @functools.lru_cache()
    def get_travis_file(self, branch):
        return self._get_file(branch=branch, FileClass=TravisYML)

    @functools.lru_cache()
    def get_appveyor_file(self, branch):
        return self._get_file(branch=branch, FileClass=AppveyorYML)

    @functools.lru_cache()
    def get_buildpy_file(self, branch):
        return self._get_file(branch=branch, FileClass=BuildPy)

    @functools.lru_cache()
    def get_travis_status(self, branch):
        try:
            return self.travis.get_last_build(repo=self.full_name, branch=branch)
        except Exception as e:
            if self.get_travis_file(branch=branch):
                log.error(f"Cannot get last build status from Travis "
                          f"for branch '{branch}: ({type(e)}) {e}'")
            return None

    @functools.lru_cache()
    def get_appveyor_status(self, branch):
        try:
            return self.appveyor.get_last_build(repo=self.full_name, branch=branch)
        except Exception as e:
            if self.get_appveyor_file(branch=branch):
                log.error(f"Cannot get last build status from Appveyor "
                          f"for branch '{branch}: ({type(e)}) {e}'")
            return None

    """
    @functools.lru_cache()
    def get_bintray_repo(self):
        try:
            _, id = self.id.split('-')
            return self.bintray.get_repository(name=id, user='conan')
        except Exception:
            return None

    @functools.lru_cache()
    def get_bintray_package(self, branch):
        try:
            _, version = branch.split('/')
            _, id = self.id.split('-')
            return self.bintray.get_package(name=id, version=version, user='conan', channel='stable')
        except Exception:
            return None
    """


if __name__ == "__main__":
    import os
    import argparse
    from conan_community_utils.github.api import api_object as g

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

    g_repo = g.get_repo(repo, lazy=False)
    r = Recipe(g_repo)

    print(f"Recipe: {r}")
    print(f" - is_recipe: {r.is_recipe(r.id)}")
    print(f" - branches: {r.get_branches()}")
    print(f" - default_branch: {r.default_branch}")
    print(f" - description: {r.description}")
    print(f" - homepage: {r.homepage}")
    print(f" - topics: {r.get_topics()}")

    for br in branches:
        print(f" - branch: {br}")
        print(f"\tis_relase_branch: {r.is_release_branch(branch=br)}")
        print(f"\tconanfile: {r.get_conanfile_file(branch=br).name}")
        print(f"\ttravis: {r.get_travis_file(branch=br).name}")
        print(f"\tappveyor: {r.get_appveyor_file(branch=br).name}")
        print(f"\treadme: {r.get_readme_file(branch=br).name}")
        print(f"\tbuild.py: {r.get_buildpy_file(branch=br).name}")
        print(f"\ttravis_status: {r.get_travis_status(branch=br)}")
        print(f"\tappveyor_status: {r.get_appveyor_status(branch=br)}")
