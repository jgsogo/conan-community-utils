
import codecs
from jinja2 import Environment, PackageLoader, select_autoescape


env = Environment(loader=PackageLoader('conan_community_utils', 'templates'),
                  autoescape=select_autoescape(['html', 'xml']))


def render(candidates, context, output_file=None):
    template = env.get_template(candidates)
    output = template.render(**context)
    if output_file:
        with codecs.open(output_file, mode='w', encoding='utf-8') as f:
            f.write(output)
    return output
