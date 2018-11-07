
import os
import shutil

from github import Github

from conan_community_utils.models.github.organization import Organization
from conan_community_utils import templates

from .organization import OrganizationHTML

import logging
log = logging.getLogger(__name__)

me = os.path.dirname(__file__)


def rate_limits(g):
    rates = g.rate_limiting
    if rates[0] < 4000:
        print("Rate limits!!!")
        print("Calls: {}".format(g.rate_limiting))
        from datetime import datetime
        print("Reset rate: {}".format(datetime.fromtimestamp(g.rate_limiting_resettime)))
        print("now: {}".format(datetime.now()))
    if rates[0] == 0:
        exit(0)


def generate_html(name, output_folder, base_url, force=False):
    # Get access to Github (do not delete things before checking credentials)
    gh = Github(os.getenv("GITHUB_TOKEN"))
    rate_limits(gh)
    log.debug("Authenticated in Github as user '{}".format(gh.get_user().name))

    # Work on output folder
    output_folder = os.path.abspath(output_folder)
    log.info("Generate HTML for community '{}' in '{}'".format(name, output_folder))

    if os.path.exists(output_folder):
        if not force:
            raise RuntimeError("Output folder '{}' already exists. Delete it or use 'force'")
        else:
            log.warning("Delete output folder '{}'".format(output_folder))
            shutil.rmtree(output_folder, ignore_errors=True)
    os.makedirs(output_folder, exist_ok=False)

    # Copy assets
    templates.copy_assets(output_folder)

    # Get organization
    org = gh.get_organization(login=name)
    org = OrganizationHTML(github_org=org, base_url=base_url)
    index = org.render(output_folder=output_folder)
    log.info("HTML index: {}".format(index))

    for recipe in org.get_recipes():
        log.info("Rendering recipe '{}'".format(recipe))
        recipe.render(output_folder=output_folder)

    return index


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate HTML.')
    parser.add_argument('--base_url', help='url path', required=True)

    args = parser.parse_args()


    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('urllib3').setLevel(level=logging.ERROR)
    logging.getLogger('github').setLevel(level=logging.ERROR)

    name = 'conan-community'
    base_url = args.base_url
    target_branch = 'master'
    output_folder = os.path.join(me, '..', '..', '..', 'tmp', 'html')
    #base_url = output_folder + "/"
    force = True

    index = generate_html(name, output_folder, base_url, force)

    gh = Github(os.getenv("GITHUB_TOKEN"))
    repo = gh.get_repo("jgsogo/conan-community-web")
    repo.create_file("")


