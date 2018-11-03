
import os
from functools import partial

from conan_community_utils.models import github
from conan_community_utils.models import travis
from conan_community_utils.models import appveyor
from conan_community_utils.views.html._html_mixin import HTMLMixin


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
APPVEYOR_TOKEN = os.getenv("APPVEYOR_TOKEN")


class RecipeHTML(HTMLMixin, github.Recipe):
    detail_url = '{self.id}/detail.html'
    template_name = 'html/recipe_detail.html'

    def __init__(self, organization, *args, **kwargs):
        super(RecipeHTML, self).__init__(*args, **kwargs)
        self._organization = organization

    @property
    def external_url(self):
        return self.github_url

    @property
    def github(self):
        return self

    @property
    def travis(self):
        if not hasattr(self, '_travis'):
            t = travis.Travis(GITHUB_TOKEN)
            t.RepositoryClass = partial(RecipeTravisHTML, recipe=self, base_url=self._base_url)
            travis_repo = t.get_repository(full_name=self._repo.full_name)
            #assert self.id == travis_repo.id, "{} != {}".format(self.id, travis_repo.id)
            assert self.full_name == travis_repo.full_name, \
                "{} != {}".format(self.full_name, travis_repo.full_name)
            setattr(self, '_travis', travis_repo)
        return getattr(self, '_travis')

    @property
    def appveyor(self):
        if not hasattr(self, '_appveyor'):
            t = appveyor.AppVeyor(APPVEYOR_TOKEN)
            t.ProjectClass = partial(RecipeAppveyorHTML, recipe=self, base_url=self._base_url)
            appveyor_repo = t.get_project(full_name=self._repo.full_name)
            setattr(self, '_appveyor', appveyor_repo)
        return getattr(self, '_appveyor')

    def get_context(self, **context):
        context = super(RecipeHTML, self).get_context(**context)
        context.update({'recipe': self,
                        'organization': self._organization,
                        'travis': self.travis})
        return context

    def render(self, output_folder):
        detail_html = super(RecipeHTML, self).render(output_folder=output_folder)
        self.travis.render(output_folder=output_folder)
        self.appveyor.render(output_folder=output_folder)
        return detail_html


class RecipeTravisHTML(HTMLMixin, travis.Repository):
    detail_url = '{self.id}/detail/travis.html'
    template_name = 'html/recipe_detail_travis.html'

    def __init__(self, recipe, *args, **kwargs):
        super(RecipeTravisHTML, self).__init__(*args, **kwargs)
        self._recipe = recipe

    @property
    def external_url(self):
        return self.travis_url

    def get_context(self, **context):
        context = super(RecipeTravisHTML, self).get_context(**context)
        context.update({'recipe': self._recipe,
                        'travis': self,
                        'organization': self._recipe._organization})
        return context


class RecipeAppveyorHTML(HTMLMixin, appveyor.Project):
    detail_url = '{self.id}/detail/appveyor.html'
    template_name = 'html/recipe_detail_appveyor.html'

    def __init__(self, recipe, *args, **kwargs):
        super(RecipeAppveyorHTML, self).__init__(*args, **kwargs)
        self._recipe = recipe

    @property
    def external_url(self):
        return self.appveyor_url

    def get_context(self, **context):
        context = super(RecipeAppveyorHTML, self).get_context(**context)
        context.update({'recipe': self._recipe,
                        'appveyor': self,
                        'organization': self._recipe._organization})
        return context

