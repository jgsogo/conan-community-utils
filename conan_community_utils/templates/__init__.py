
import os
import shutil
import codecs
import datetime
from pprint import pformat
from jinja2 import Environment, PackageLoader, select_autoescape
from markupsafe import Markup
from functools import partial


env = Environment(loader=PackageLoader('conan_community_utils', 'templates'),
                  autoescape=select_autoescape(['html', 'xml']))


def html_warning(msg):
    return Markup(f'<span class="dot dot-warning" title="{msg}"></span>')


def html_error(msg):
    return Markup(f'<span class="dot dot-error" title="{msg}"></span>')


def check_equal(lhs, rhs, msg=None, level="warning"):
    if lhs != rhs:
        level_str = "Warning" if level == "warning" else "Error"
        msg = msg.format(lhs=lhs, rhs=rhs) if msg else f"{level_str}: '{lhs}' != '{rhs}'"
        return html_warning(msg) if level == "warning" else html_error(msg)
    return ''


def check_true(item, msg=None, level="warning"):
    if not item:
        level_str = "Warning" if level == "warning" else "Error"
        msg = msg.format(item=item) if msg else f"{level_str}: '{item}' is not True"
        return html_warning(msg) if level == "warning" else html_error(msg)
    return ''


def check_false(item, msg=None, level="warning"):
    if item:
        level_str = "Warning" if level == "warning" else "Error"
        msg = msg.format(item=item) if msg else f"{level_str}: '{item}' is not False"
        return html_warning(msg) if level == "warning" else html_error(msg)
    return ''


def render(candidates, context, output_file=None):
    template = env.get_template(candidates)
    template.globals['now'] = datetime.datetime.utcnow
    template.globals['warning_eq'] = partial(check_equal, level="warning")
    template.globals['error_eq'] = partial(check_equal, level="error")
    template.globals['warning_true'] = partial(check_true, level="warning")
    template.globals['error_true'] = partial(check_true, level="error")
    template.globals['warning_false'] = partial(check_false, level="warning")
    template.globals['error_false'] = partial(check_false, level="error")
    template.globals['pprint'] = pformat
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
