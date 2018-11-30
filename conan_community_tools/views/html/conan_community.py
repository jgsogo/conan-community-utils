
import os
import shutil
from datetime import datetime, timedelta
from github import Github

from conan_community_tools import templates
from conan_community_tools.views.html.organization import OrganizationHTML

import logging
log = logging.getLogger(__name__)


def rate_limits(g, raise_at=500):
    rates = g.rate_limiting
    reset_in = datetime.fromtimestamp(g.rate_limiting_resettime)-datetime.now()
    reset_in = reset_in - timedelta(microseconds=reset_in.microseconds)
    log.info(f"Rate limit: {rates[0]}/{rates[1]} (reset in {reset_in})")
    if raise_at and rates[0] <= raise_at:
        raise RuntimeError(f"Rate limit under {raise_at}!")


def generate_html(name, output_folder, base_url, force=False):
    # Get access to Github (do not delete things before checking credentials)
    gh = Github(os.getenv("GITHUB_TOKEN"))
    rate_limits(gh, raise_at=100)
    log.debug(f"Authenticated in Github as user '{gh.get_user().name}")

    # Work on output folder
    output_folder = os.path.abspath(output_folder)
    log.info(f"Generate HTML for community '{name}' in '{output_folder}'")

    if os.path.exists(output_folder):
        if not force:
            raise RuntimeError(f"Output folder '{output_folder}' already exists. Delete it or use 'force'")
        else:
            log.warning(f"Delete output folder '{output_folder}'")
            shutil.rmtree(output_folder, ignore_errors=True)
    os.makedirs(output_folder, exist_ok=False)

    # Copy assets
    templates.copy_assets(output_folder)

    # Get organization
    org = gh.get_organization(login=name)
    org = OrganizationHTML(github_org=org, base_url=base_url)
    all_recipes = org.get_recipes()

    errors = []
    for recipe in all_recipes:
        try:
            rate_limits(gh, raise_at=500)
            log.info(f"Rendering recipe '{recipe}'")
            recipe.render(output_folder=output_folder, all_recipes=all_recipes)
        except Exception as e:
            msg = f">> ERROR rendering recipe '{recipe}': ({type(e)}) {e}"
            errors.append([str(recipe), msg])
            log.error(msg)
            import traceback
            traceback.print_exc()

    index = org.render(output_folder=output_folder, errors=errors, all_recipes=all_recipes)
    log.info(f"HTML index: {index}")

    return index


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate HTML.')
    parser.add_argument('--base_url', help='url path', required=True)

    args = parser.parse_args()


    logging.basicConfig(level=logging.INFO)
    logging.getLogger('urllib3').setLevel(level=logging.ERROR)
    logging.getLogger('github').setLevel(level=logging.ERROR)

    name = 'conan-community'
    base_url = args.base_url
    target_branch = 'master'

    me = os.path.dirname(__file__)
    output_folder = os.path.join(me, '..', '..', '..', '..', 'tmp')
    #base_url = output_folder + "/"
    force = True

    index = generate_html(name, output_folder, base_url, force)
