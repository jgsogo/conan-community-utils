
import os
import sys
import argparse
import logging
from datetime import datetime, timedelta
import yaml
import shutil
import re

from conan_community_tools.github.api import get_client as get_github_client
from conan_community_tools.ci.travis import get_client as get_travis_client
from conan_community_tools.ci.appveyor import get_client as get_appveyor_client
from conan_community_tools.storages.bintray.api import get_client as get_bintray_client

from conan_community_tools.templates import copy_assets
from conan_community_tools.views.html.organization import OrganizationHTML


log = logging.getLogger('conan_community_tools')


class CLIFormatter(logging.Formatter):  # pragma: no cover
    max_length = 10

    def format(self, record):
        try:
            name = record.__dict__['name'].split('.', 1)[1]
            record.name = '~.{}'.format(name)
            return super(CLIFormatter, self).format(record)
        except:
            record.name = '~.'
            return super(CLIFormatter, self).format(record)


def check_required_tokens(config):
    # Github
    gh_client = get_github_client()
    sys.stdout.write(f"Github: authenticated as user '{gh_client.get_user().name}'\n")
    rates = gh_client.rate_limiting
    reset_in = datetime.fromtimestamp(gh_client.rate_limiting_resettime) - datetime.now()
    reset_in = reset_in - timedelta(microseconds=reset_in.microseconds)
    sys.stdout.write(f" - rate limit: {rates[0]}/{rates[1]}\n")
    sys.stdout.write(f" - time to reset: {reset_in}\n")

    # Travis
    travis_client = get_travis_client()
    user_info = travis_client.get_user()
    sys.stdout.write(f"Travis: connected as user '{user_info['name']}'\n")

    # Appveyor
    appveyor_client = get_appveyor_client()
    users = appveyor_client.get_users()
    sys.stdout.write(f"Appveyor: connected as user ")
    for it in users:
        if it['isOwner']:
            sys.stdout.write(f"'{it['fullName']}'\n")

    # Bintray
    bintray_client = get_bintray_client(config=config)
    user = bintray_client.get_user_info()
    sys.stdout.write(f"Bintray: connected as user '{user['name']}'\n")


def main():
    sys.stdout.write("=== Conan - Community Web ===\n")

    parser = argparse.ArgumentParser(description='Generate static web page')
    parser.add_argument('configuration', help='Path to config.yml')
    parser.add_argument("-v", "--verbose", dest="verbose_count",
                        action="count", default=0,
                        help="increases log verbosity for each occurence.")
    parser.add_argument("--local", dest="local",
                        action='store_true', default=False,
                        help="If we are running local, base_url will be equal to output-path")
    #parser.add_argument('--base-url', help='URL to webpage', required=True)
    parser.add_argument('--output-path', dest='output_path',
                        help='Path to store generated content', required=True)
    parser.add_argument("--force", dest="force",
                        action='store_true', default=False,
                        help="Delete output folder if it already exists")
    args = parser.parse_args()

    # Configure logging
    my_formatter = CLIFormatter('[%(levelname)-8s] %(name)-20s (%(lineno)d): %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(my_formatter)
    # logging.basicConfig(stream=sys.stderr, level=logging.INFO,
    #                    format='[%(levelname)-8s] %(name)s (%(lineno)d): %(message)s')
    log.setLevel(max(3 - args.verbose_count, 0) * 10)
    log.addHandler(handler)

    # Check that the file exists
    configuration = os.path.abspath(args.configuration)
    if not os.path.exists(configuration):
        sys.stderr.write(f"Configuration '{configuration}' does not exists or it is inaccessible\n")
        exit(-1)

    try:
        # Parse configuration file
        with open(configuration) as f:
            config = yaml.load(f.read())

        # Check required environment variables (connections to APIs)
        check_required_tokens(config=config)

        # Handle output path
        output_path = os.path.abspath(args.output_path)
        if os.path.exists(output_path):
            if not args.force:
                raise RuntimeError(
                    f"Output path '{output_path}' already exists. Delete it or use '--force'")
            else:
                log.warning(f"Delete output path '{output_path}'")
                shutil.rmtree(output_path, ignore_errors=True)
        os.makedirs(output_path, exist_ok=False)

        base_url = config['base_url']
        if args.local:
            base_url = output_path
        if not base_url[-1] == '/':
            base_url += '/'
        copy_assets(output_path)

        # Get organization
        org = OrganizationHTML(name=config['organization']['name'], base_url=base_url, config=config)
        sys.stdout.write(f"Work on organization: {org}\n")
        sys.stdout.write(f" - base_url: {org._base_url}\n")
        recipe_pattern = config['organization'].get('recipe_pattern', 'conan-[\w_]+')
        sys.stdout.write(f" - recipe_pattern: {recipe_pattern}\n")
        recipe_pattern = re.compile(recipe_pattern)

        # Work on recipes
        errors = []
        all_recipes = org.get_recipes(re_pattern=recipe_pattern)
        for i, recipe in enumerate(all_recipes, 1):
            sys.stdout.write(f"[{i}/{len(all_recipes)}] {recipe}\n")
            try:
                recipe.render(output_folder=output_path, all_recipes=all_recipes)
            except Exception as e:
                msg = f">> ERROR rendering recipe '{recipe}': ({type(e)}) {e}"
                errors.append([str(recipe), msg])
                sys.stderr.write(msg + "\n")

                import traceback
                log.debug(traceback.format_exc())

        index = org.render(output_folder=output_path, errors=errors, all_recipes=all_recipes)
        sys.stdout.write(f"HTML index: {index}\n")

    except KeyboardInterrupt:
        sys.stdout.write("User interrupted. Ok")
    except Exception as e:
        sys.stderr.write(f"Unhandled error ({type(e)}): {e}")
        import traceback
        traceback.print_exc()

    sys.stdout.write("=====\n")
    return


if __name__ == '__main__':
    main()
