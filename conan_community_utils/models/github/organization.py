
import functools
from github.Organization import Organization as github_Organization

from conan_community_utils.utils.lazy_property import lazy_property
from .recipe import Recipe
import logging

log = logging.getLogger(__name__)


class Organization(object):
    RecipeClass = Recipe

    def __init__(self, github_org):
        assert isinstance(github_org, github_Organization)
        self._github_org = github_org

    def __str__(self):
        return self.id

    @property
    def id(self):
        return self._github_org.name

    @functools.lru_cache()
    def get_recipes(self):
        ret = []
        for repo in self._github_org.get_repos('all')[6:10]:
            if Recipe.is_recipe(repo.name):
                ret.append(self.RecipeClass(repo=repo))
            else:
                log.debug("Repository '{}/{}' discarded as recipe".format(self, repo.name))
        return ret
