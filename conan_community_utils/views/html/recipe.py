
import os
import functools
from slugify import slugify
from collections import defaultdict

from conan_community_utils.models import github
from conan_community_utils.views.html._html_mixin import HTMLMixin
from conan_community_utils.templates import render_check

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

        def __count_warnings_errors(str_triage):
            nonlocal n_warnings
            nonlocal n_errors
            n_warnings += 1 if str_triage == 'warning' else 0
            n_errors += 1 if str_triage == 'error' else 0

        if branch is False:
            ret = defaultdict(dict)
            n_warnings = 0
            n_errors = 0

            # Github configuration
            def _row(field, test, if_fail='error', msg_ok='ok', msg_fail='fail'):
                assert if_fail in ['error', 'warning']
                str_triage = 'ok' if test else if_fail
                str_msg = msg_ok if str_triage == 'ok' else msg_fail
                __count_warnings_errors(str_triage)
                return field, render_check(str_triage, str_msg), str_msg

            github_project = {'headers': None,
                              'rows': [
                                  _row('Issues', not self._repo.has_issues, 'warning', msg_fail='Remove issues tab from Github'),
                                  _row('Projects', not self._repo.has_projects, 'warning', msg_fail='Remove projects tab from Github'),
                                  _row('Wiki', not self._repo.has_wiki, 'warning', msg_fail='Remove wiki tab from Github'),
                                  _row('Topics', self.get_topics(), 'warning', msg_fail='Add topics to Github repository'),
                                  _row('Homepage', self._repo.homepage, 'warning', msg_fail='Add homepage to underlying library'),
                                  _row('Description', self._repo.description, 'warning', msg_fail='Add description to repository'),
                              ]}
            ret['Github project configuration'] = github_project

            # Github meta -vs- Bintray meta
            def _row(field, lhs, rhs, if_fail='error', msg_ok='ok', msg_fail='fail'):
                assert if_fail in ['error', 'warning']
                str_triage = 'ok' if lhs == rhs else if_fail
                str_msg = msg_ok if str_triage == 'ok' else msg_fail
                __count_warnings_errors(str_triage)
                return field, render_check(str_triage, str_msg), lhs, rhs

            bintray_repo = self.get_bintray_repo()
            if bintray_repo:
                github_bintray = {'headers': ['', '', 'Github', 'Bintray'],
                                  'rows': [
                                      ['name', '', self._repo.name, bintray_repo['name']],
                                      _row('Description', self._repo.description, bintray_repo["desc"], 'error'),
                                      _row('Homepage', self._repo.homepage, bintray_repo["website_url"], 'error'),
                                      _row('Topics', self.get_topics(), bintray_repo["labels"], 'error'),
                                      _row('License', self.get_license(), bintray_repo["licenses"], 'error'),
                                  ]}

                ret['Github project -vs- Bintray'] = github_bintray

            return ret, n_warnings, n_errors

        elif branch is None:
            ret = defaultdict(dict)
            n_warnings = 0
            n_errors = 0

            _ret, _n_warnings, _n_errors = self._grab_warnings(branch=False)
            ret[None] = _ret
            n_warnings += _n_warnings
            n_errors += _n_errors

            for it in self.get_branches():
                _ret, _n_warnings, _n_errors = self._grab_warnings(branch=it)
                ret[it] = _ret
                n_warnings += _n_warnings
                n_errors += _n_errors

            return ret, n_warnings, n_errors

        else:
            ret = defaultdict(dict)
            n_warnings = 0
            n_errors = 0

            # Conanfile -vs- Bintray repo
            conanfile = self.get_conanfile(branch=branch)
            bintray_pck = self.get_bintray_package(branch=branch)

            rows = []
            if not conanfile:
                rows.append([render_check('error', 'error'), f"Branch {branch} doesn't have a conanfile!"])
                __count_warnings_errors('error')

            if self.is_release_branch(branch_name=branch) and not bintray_pck:
                rows.append([render_check('error', 'error'), f"Cannot get repository in Bintray for branch {branch} (and it is a release branch)!"])
                __count_warnings_errors('error')

            if rows:
                ret['Errors'] = {'headers': None, 'rows': rows}

            if conanfile and bintray_pck:
                def _row(field, lhs, rhs, if_fail='error', msg_ok='ok', msg_fail='fail'):
                    assert if_fail in ['error', 'warning']
                    str_triage = 'ok' if lhs == rhs else if_fail
                    str_msg = msg_ok if str_triage == 'ok' else msg_fail
                    __count_warnings_errors(str_triage)
                    return field, render_check(str_triage, str_msg), lhs, rhs

                bintray_conanfile = {'headers': ['', '', f'conanfile @ {branch}', 'Bintray'],
                                     'rows': [
                                         _row('Name', conanfile._attribs['name'], bintray_pck.name, 'error'),
                                         _row('Version', conanfile._attribs['version'], bintray_pck.version, 'error'),
                                         _row('Url', conanfile._attribs.get('url', None), bintray_pck._json['vcs_url'], 'error'),
                                         _row('Homepage', conanfile._attribs.get('homepage', None), bintray_pck._json['website_url'], 'error'),
                                         _row('Topics', conanfile._attribs.get('topics', None), bintray_pck._json['labels'], 'error'),
                                         _row('License', conanfile._attribs.get('license', None), bintray_pck._json['licenses'], 'error'),
                                         _row('Description', conanfile._attribs.get('description', None), bintray_pck._json['desc'], 'error'),

                                     ]}
                ret['conanfile.py -vs- Bintray'] = bintray_conanfile
            return ret, n_warnings, n_errors

    @functools.lru_cache()
    def count_errors(self, branch=None):
        all, n_warnings, n_errors = self._grab_warnings(branch=branch)
        return n_errors

    @functools.lru_cache()
    def count_warnings(self, branch=None):
        all, n_warnings, n_errors = self._grab_warnings(branch=branch)
        return n_warnings

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
