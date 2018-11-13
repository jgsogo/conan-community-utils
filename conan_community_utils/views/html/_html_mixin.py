import os

from conan_community_utils import templates

import logging
log = logging.getLogger(__name__)


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

    def render(self, output_folder, **context):
        output_filename = os.path.join(output_folder, self.get_detail_url())
        template_name = self.get_template_name()
        templates.render(template_name, context=self.get_context(**context),
                         output_file=output_filename)
        log.debug(f"> Generated '{output_filename}'")
        return output_filename

    def dump(self):
        from pprint import pformat
        return pformat(vars(self))
