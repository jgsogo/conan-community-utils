
import os
from functools import partial, partialmethod
from slugify import slugify
from urllib.parse import quote

from conan_community_utils.models import github
#from conan_community_utils.models import travis
#from conan_community_utils.models import appveyor
from conan_community_utils.views.html._html_mixin import HTMLMixin

import logging
log = logging.getLogger(__name__)


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
APPVEYOR_TOKEN = os.getenv("APPVEYOR_TOKEN")


class RecipeHTML(HTMLMixin, github.Recipe):
    detail_url = '{self.id}/detail/{branch}.html'

    def __init__(self, organization, *args, **kwargs):
        super(RecipeHTML, self).__init__(*args, **kwargs)
        self._organization = organization
        self.branches = self.get_branches()  # [br for br in self.get_branches() if github.Recipe.is_release_branch(br)]
        self.main_branch = self.branches[0]
        self.active_branch = None

    @property
    def external_url(self):
        return self.github_url

    @property
    def url(self):
        return self.get_url(branch=None)

    def get_url(self, branch=None):
        return os.path.join(self._base_url, self.get_detail_url(branch=branch))

    def get_detail_url(self, branch=None):
        branch = branch if branch is not None else self.active_branch
        if branch:
            detail_url = self.detail_url.format(self=self, branch=slugify(branch))
            return detail_url
        else:
            detail_url = self.detail_url.format(self=self, branch="index")
            return detail_url

    def get_template_name(self):
        if self.active_branch:
            return 'html/recipe_detail_branch.html'
        else:
            return 'html/recipe_detail.html'

    def get_context(self, **context):
        context = super(RecipeHTML, self).get_context(**context)
        context.update({'recipe': self,
                        'organization': self._organization, })
        return context

    def render(self, output_folder):
        log.debug(f"Render recipe detail '{self.id}'")
        html = super().render(output_folder=output_folder)

        for branch in self.get_branches():
            self.active_branch = branch
            log.debug(f"Render recipe detail '{self.id}' for branch '{self.active_branch}'")
            super().render(output_folder=output_folder)
        self.active_branch = None
        return html
