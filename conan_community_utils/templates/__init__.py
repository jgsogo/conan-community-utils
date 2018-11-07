
import os
import shutil
import codecs
import datetime
from jinja2 import Environment, PackageLoader, select_autoescape


env = Environment(loader=PackageLoader('conan_community_utils', 'templates'),
                  autoescape=select_autoescape(['html', 'xml']))


def render(candidates, context, output_file=None):
    template = env.get_template(candidates)
    template.globals['now'] = datetime.datetime.utcnow
    output = template.render(**context)
    if output_file:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with codecs.open(output_file, mode='w', encoding='utf-8') as f:
            f.write(output)
    return output


def copy_assets(output_folder):
    me = os.path.dirname(__file__)
    shutil.copytree(src=os.path.join(me, 'assets', 'js'), dst=os.path.join(output_folder, 'js'))
    shutil.copytree(src=os.path.join(me, 'assets', 'css'), dst=os.path.join(output_folder, 'css'))
