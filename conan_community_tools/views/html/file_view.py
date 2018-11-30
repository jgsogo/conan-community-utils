
from ._html_mixin import HTMLMixin


class FileViewHTML(HTMLMixin):
    template_name = 'html/file_view.html'

    def __init__(self, obj_file, recipe, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._obj_file = obj_file
        self._parent_recipe = recipe

    def get_detail_url(self):
        recipe_detail_url = self._parent_recipe.get_detail_url()
        return recipe_detail_url.replace(".html", "_file.html")

    def get_context(self, **context):
        context = super().get_context(object=self._parent_recipe, **context)
        context.update(self._parent_recipe.get_context(**context))
        context.update({'base_html': self._parent_recipe.get_template_name(),
                        'file': self._obj_file})
        return context

