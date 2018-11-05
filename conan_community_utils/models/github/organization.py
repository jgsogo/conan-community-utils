
from github.Organization import Organization as github_Organization

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

    def get_recipes(self):
        for repo in self._github_org.get_repos('all'):
            if Recipe.is_recipe(repo.name):
                yield self.RecipeClass(repo=repo)
            else:
                log.debug("Repository '{}/{}' discarded as recipe".format(self, repo.name))
