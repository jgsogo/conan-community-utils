
import os
from functools import partial

from conan_community_utils import templates

from conan_community_utils.models.github.organization import Organization
from conan_community_utils.models.github.recipe import Recipe


class HTMLMixin(object):
    detail_url = None
    template_name = None

    def __init__(self, base_url, *args, **kwargs):
        self._base_url = base_url
        super(HTMLMixin, self).__init__(*args, **kwargs)

    @property
    def url(self):
        return os.path.join(self._base_url, self.get_detail_url())

    def get_detail_url(self):
        if not self.detail_url:
            raise RuntimeError("No 'self.detail_url' given or self.get_detail_url() overriden")
        detail_url = self.detail_url.format(self=self)
        return detail_url

    def get_context(self, **context):
        if 'base_url' not in context:
            context['base_url'] = self._base_url
        if 'object' not in context:
            context['object'] = self
        return context

    def get_template_name(self):
        if not self.template_name:
            raise RuntimeError("No 'self.template_name' given or self.get_template_name() overriden")
        return self.template_name

    def render(self, output_folder):
        output_filename = os.path.join(output_folder, self.get_detail_url())
        templates.render(self.get_template_name(), context=self.get_context(),
                         output_file=output_filename)
        return output_filename


class RecipeHTML(HTMLMixin, Recipe):
    detail_url = '{self.id}/detail.html'
    template_name = 'html/recipe_detail.html'

    def __init__(self, organization, *args, **kwargs):
        super(RecipeHTML, self).__init__(*args, **kwargs)
        self._organization = organization

    def get_context(self, **context):
        context = super(RecipeHTML, self).get_context(**context)
        context.update({'recipe': self,
                        'organization': self._organization})
        return context


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
