
import os
from functools import partial

from conan_community_utils.models.github.recipe import Recipe
from conan_community_utils.models.travis.repository import Repository
from conan_community_utils.models.travis.travis import Travis
from conan_community_utils.views.html._html_mixin import HTMLMixin


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


class RecipeHTML(HTMLMixin, Recipe):
    detail_url = '{self.id}/detail.html'
    template_name = 'html/recipe_detail.html'

    def __init__(self, organization, *args, **kwargs):
        super(RecipeHTML, self).__init__(*args, **kwargs)
        self._organization = organization

    @property
    def github(self):
        return self

    @property
    def travis(self):
        if not hasattr(self, '_travis'):
            travis = Travis(GITHUB_TOKEN)
            travis.RepositoryClass = partial(RecipeTravisHTML, recipe=self, base_url=self._base_url)
            travis_repo = travis.get_repository(full_name=self._repo.full_name)
            assert self.id == travis_repo.id, "{} != {}".format(self.id, travis_repo.id)
            assert self.full_name == travis_repo.full_name, \
                "{} != {}".format(self.full_name, travis_repo.full_name)
            setattr(self, '_travis', travis_repo)
        return getattr(self, '_travis')

    def get_context(self, **context):
        context = super(RecipeHTML, self).get_context(**context)
        context.update({'recipe': self,
                        'organization': self._organization,
                        'travis': self.travis})
        return context

    def render(self, output_folder):
        detail_html = super(RecipeHTML, self).render(output_folder=output_folder)
        self.travis.render(output_folder=output_folder)
        return detail_html


class RecipeTravisHTML(HTMLMixin, Repository):
    detail_url = '{self.id}/detail/travis.html'
    template_name = 'html/recipe_detail_travis.html'

    def __init__(self, recipe, *args, **kwargs):
        super(RecipeTravisHTML, self).__init__(*args, **kwargs)
        self._recipe = recipe

    def get_context(self, **context):
        context = super(RecipeTravisHTML, self).get_context(**context)
        context.update({'recipe': self._recipe,
                        'travis': self,
                        'organization': self._recipe._organization})
        return context

