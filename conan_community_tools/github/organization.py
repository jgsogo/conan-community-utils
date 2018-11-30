
import functools
from .api import get_client
from .recipe import Recipe

import logging
log = logging.getLogger(__name__)


class Organization(object):
    RecipeClass = Recipe

    def __init__(self, name):
        self._gh = get_client()
        self._github_org = self._gh.get_organization(login=name)

    def __str__(self):
        return self.id

    @property
    def id(self):
        return self._github_org.name

    @functools.lru_cache()
    def get_recipes(self, re_pattern=None):
        ret = []
        for repo in self._github_org.get_repos('all'):
            if re_pattern and not re_pattern.match(repo.name):
                log.info(f"Repo '{repo.name}' discarded by organization recipe pattern")
            else:
                ret.append(self.RecipeClass(repo=repo))
        return ret


if __name__ == "__main__":
    import os
    import argparse

    parser = argparse.ArgumentParser(description='Run github/organization example')
    parser.add_argument('--organization', help='Organization name')
    parser.add_argument("-v", "--verbose", dest="verbose_count",
                        action="count", default=0,
                        help="increases log verbosity for each occurence.")
    args = parser.parse_args()

    organization = args.organization or 'conan-community'
    log_level = max(3 - args.verbose_count, 0) * 10

    # Configure logging
    logging.basicConfig(level=log_level)
    logging.getLogger('urllib3').setLevel(level=logging.ERROR)
    logging.getLogger('github').setLevel(level=logging.ERROR)

    org = Organization(organization)
    print(f"Organization: {org}")
    for r in org.get_recipes():
        print(f"- recipe: {r}")
