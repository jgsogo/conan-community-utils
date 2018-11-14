
import os
import re
import functools
from github.Repository import Repository as github_Repository

from conan_community_utils.models.travis import Travis
from conan_community_utils.models.appveyor import Appveyor
from conan_community_utils.models.bintray import Bintray
from conan_community_utils.utils.file_view import FileView
from conan_community_utils.models.github.conanfile import ConanFile

import logging
log = logging.getLogger(__name__)


class Readme(FileView):
    name = "README.md"
    language = 'markdown'


class Recipe(object):
    """ Models a conan recipe in Github """

    travis = Travis(token=os.getenv("TRAVIS_TOKEN"))
    appveyor = Appveyor(token=os.getenv("APPVEYOR_TOKEN"))
    bintray = Bintray(api_token=os.getenv("BINTRAY_TOKEN"), api_username=os.getenv("BINTRAY_USERNAME"))

    def __init__(self, repo):
        assert isinstance(repo, github_Repository)
        self._repo = repo

    def __str__(self):
        return self.id

    @classmethod
    def is_recipe(cls, repo_name):
        return bool(re.match(r"conan-[\w_]+", repo_name, re.IGNORECASE))

    @classmethod
    def is_release_branch(cls, branch_name):
        return bool(re.match(r"release/[a-zA-Z0-9_][a-zA-Z0-9_+.-]+", branch_name)) or \
               bool(re.match(r"stable/[a-zA-Z0-9_][a-zA-Z0-9_+.-]+", branch_name))

    @property
    def id(self):
        return str(self._repo.name)

    @property
    def full_name(self):
        return self._repo.full_name

    #@property
    #def github_url(self):
    #    return self._repo.html_url  # TODO: git_url

    @functools.lru_cache()
    def get_branches(self):
        return [branch.name for branch in self._repo.get_branches()]

    @functools.lru_cache()
    def get_topics(self):
        return self._repo.get_topics()

    @functools.lru_cache()
    def get_conanfile(self, branch):
        try:
            content = self._repo.get_contents("conanfile.py", ref=branch).decoded_content.decode("utf-8")
            conanfile = ConanFile(content=content)
            return conanfile
        except Exception as e:
            log.error(f"Cannot retrieve 'conanfile.py' (repo {self.full_name}) from branch {branch}: ({type(e)}) {e}")
            return None

    @functools.lru_cache()
    def get_readme(self, branch):
        try:
            content = self._repo.get_contents("README.md", ref=branch).decoded_content.decode("utf-8")
            readme = Readme(content=content)
            return readme
        except Exception as e:
            log.error(f"Cannot retrieve 'README.md' (repo {self.full_name}) from branch {branch}: ({type(e)}) {e}")
            return None

    @functools.lru_cache()
    def get_license(self):
        try:
            return self._repo.get_license()
        except Exception as e:
            log.error(f"Cannot retrieve license (repo {self.full_name}): ({type(e)}) {e}")
            return None

    @functools.lru_cache()
    def get_travis_status(self, branch):
        try:
            r = self.travis.get_last_build(self.full_name, branch=branch)
            return r.get("state", "unknown"), r['url']
        except Exception as e:
            return None, None

    @functools.lru_cache()
    def get_appveyor_status(self, branch):
        try:
            r = self.appveyor.get_last_build(repo=self.id, branch=branch)
            return r.get("status", "unknown"), r['url']
        except Exception as e:
            return None, None

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


if __name__ == "__main__":
    from github import Github

    g = Github(os.getenv("GITHUB_TOKEN"))

    print("Rate limits")
    print("Calls: {}".format(g.rate_limiting))
    from datetime import datetime
    print("Reset rate: {}".format(datetime.fromtimestamp(g.rate_limiting_resettime)))

    print("Authorized in Github for user '{}'".format(g.get_user().name))

    org = g.get_organization("conan-community").get_repos('all')
    recipes = []
    for r in org[:1]:
        if Recipe.is_recipe(r.name):
            recipes.append(Recipe(repo=r))

    # Testing some outputs
    p = os.path.join(os.path.dirname(__file__), 'tmp')
    os.makedirs(p, exist_ok=True)
    for recipe in recipes:
        #filename = recipe.render(output_folder=p, recipe_list=recipes)
        #print(filename)
        print(recipe)
        print(recipe._repo.html_url)
        for branch in recipe.get_branches():
            print(" - {} is release {}".format(branch, Recipe.is_release_branch(branch)))
            if Recipe.is_release_branch(branch):
                conanfile = recipe.get_conanfile(branch=branch)
                print(conanfile._attribs["version"])
                print(recipe.get_travis_status(branch=branch))
                print(recipe.get_appveyor_status(branch=branch))

    print("Rate limits")
    print("Calls: {}".format(g.rate_limiting))
    from datetime import datetime
    print("Reset rate: {}".format(datetime.fromtimestamp(g.rate_limiting_resettime)))