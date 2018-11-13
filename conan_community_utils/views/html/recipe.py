
import os
import functools
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

    def get_github_url(self, branch=None):
        branch = branch if branch is not None else self.active_branch
        if branch:
            return '/'.join([self._repo.html_url, 'tree', branch])
        else:
            return self._repo.html_url

    @functools.lru_cache()
    def _grab_warnings(self, branch):
        ret = []
        if branch is False:
            # Github configuration
            if self._repo.has_issues:
                ret.append(['warning', None, 'Remove issues tab from Github'])
            if self._repo.has_projects:
                ret.append(['warning', None, 'Remove projects tab from Github'])
            if self._repo.has_wiki:
                ret.append(['warning', None, 'Remove wiki tab from Github'])
            if not self.get_topics():
                ret.append(['warning', None, "Add topics to Github repository"])
            if not self._repo.homepage:
                ret.append(['warning', None, "Add homepage of underlying library"])
            if not self._repo.description:
                ret.append(['error', None, "Add description to repository"])

            # Github meta -vs- Bintray meta
            bintray_repo = self.get_bintray_repo()
            if bintray_repo:
                if self._repo.description != bintray_repo["desc"]:
                    ret.append(['error', None, "Description in Github and Bintray doesn't match"])
                if self._repo.homepage != bintray_repo["website_url"]:
                    ret.append(['error', None, "Homepage in Github and Bintray doesn't match"])
                if self.get_topics() != bintray_repo["labels"]:
                    ret.append(['error', None, "Topics in Github doesn't match labels in Bintray"])
                if self.get_license() != bintray_repo["licenses"]:
                    ret.append(['error', None, "License in Github and Bintray doesn't match"])

        elif branch is None:
            ret.extend(self._grab_warnings(branch=False))
            for it in self.get_branches():
                ret.extend(self._grab_warnings(branch=it))

        else:
            # Conanfile -vs- Bintray repo
            conanfile = self.get_conanfile(branch=branch)
            bintray_pck = self.get_bintray_package(branch=branch)

            if self.is_release_branch(branch_name=branch):
                if not conanfile:
                    ret.append(['error', branch, f"Branch {branch} doesn't have a conanfile!"])
                if not bintray_pck:
                    ret.append(['error', branch, f"Cannot get repository in Bintray!"])

            if conanfile and bintray_pck:
                if conanfile._attribs["name"] != bintray_pck.name:
                    ret.append(['error', branch, f"Different name in Bintray and Conanfile"])
                if conanfile._attribs["version"] != bintray_pck.version:
                    ret.append(['error', branch, f"Different version in Bintray and Conanfile"])
                if conanfile._attribs.get("url", None) != bintray_pck._json["vcs_url"]:
                    ret.append(['error', branch, f"Different VCS url in Bintray and Conanfile"])

                if conanfile._attribs.get("homepage", None) != bintray_pck._json["website_url"]:
                    ret.append(['error', branch, f"Different homepage in Bintray and Conanfile"])
                if conanfile._attribs.get("topics", None) != bintray_pck._json["labels"]:
                    ret.append(['error', branch, f"Different topics/labels in Bintray and Conanfile"])
                if conanfile._attribs.get("license", None) != bintray_pck._json["licenses"]:
                    ret.append(['error', branch, f"Different licenses in Bintray and Conanfile"])
                if conanfile._attribs.get("description", None) != bintray_pck._json["desc"]:
                    ret.append(['error', branch, f"Different homepage in Bintray and Conanfile"])

        return ret

    @functools.lru_cache()
    def count_errors(self, branch=None):
        all = self._grab_warnings(branch=branch)
        return sum([1 for level, branch, msg in all if level == 'error'])

    @functools.lru_cache()
    def count_warnings(self, branch=None):
        all = self._grab_warnings(branch=branch)
        return sum([1 for level, branch, msg in all if level == 'warning'])

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

    def render(self, output_folder, **context):
        log.debug(f"Render recipe detail '{self.id}'")
        html = super().render(output_folder=output_folder, **context)

        for branch in self.get_branches():
            self.active_branch = branch
            log.debug(f"Render recipe detail '{self.id}' for branch '{self.active_branch}'")
            super().render(output_folder=output_folder, **context)
        self.active_branch = None
        return html
