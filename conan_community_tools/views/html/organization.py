from functools import partial

from conan_community_tools.github.organization import Organization
from conan_community_tools.views.html._html_mixin import HTMLMixin
from conan_community_tools.views.html.recipe import RecipeHTML


class OrganizationHTML(HTMLMixin, Organization):
    detail_url = 'index.html'
    template_name = 'html/organization_detail.html'

    @property
    def RecipeClass(self):
        return partial(RecipeHTML, base_url=self._base_url, organization=self)

    def get_context(self, **context):
        context = super(OrganizationHTML, self).get_context(**context)
        context.update({'organization': self, })
        return context
