
import os
import shutil
import codecs
import datetime
from pprint import pformat
from jinja2 import Environment, PackageLoader, select_autoescape
from markupsafe import Markup


env = Environment(loader=PackageLoader('conan_community_tools', 'templates'),
                  autoescape=select_autoescape(['html', 'xml']))


def render_check(status, msg, number=' '):
    assert status in ['error', 'warning', 'ok']
    return Markup(f'<span class="numberCircle numberCircle-{status}" title="{msg}"><span>{number}</span></span>')


def render(candidates, context, output_file=None, add_globals=None):
    template = env.get_template(candidates)
    template.globals['now'] = datetime.datetime.utcnow
    template.globals['render_check'] = render_check
    template.globals['pprint'] = pformat
    if add_globals:
        template.globals.update(add_globals)
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
