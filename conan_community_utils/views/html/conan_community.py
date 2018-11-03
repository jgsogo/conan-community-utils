
import os
import shutil

from github import Github

from conan_community_utils.models.github.organization import Organization
from conan_community_utils import templates

from .organization import OrganizationHTML

import logging
log = logging.getLogger(__name__)

me = os.path.dirname(__file__)


def generate_html(name, output_folder, base_url, force=False):
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

    # Get access to Github
    gh = Github(os.getenv("GITHUB_TOKEN"))
    log.debug("Authenticated in Github as user '{}".format(gh.get_user().name))

    # Get organization
    org = gh.get_organization(login=name)
    org = OrganizationHTML(github_org=org, base_url=base_url)
    index = org.render(output_folder=output_folder)
    log.info("HTML index: {}".format(index))

    for recipe in org.get_recipes():
        recipe.render(output_folder=output_folder)

    return index


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('urllib3').setLevel(level=logging.ERROR)
    logging.getLogger('github').setLevel(level=logging.ERROR)

    name = 'conan-community'
    output_folder = os.path.join(me, '..', '..', '..', 'tmp', 'html')
    base_url = output_folder + "/"
    force = True

    index = generate_html(name, output_folder, base_url, force)




