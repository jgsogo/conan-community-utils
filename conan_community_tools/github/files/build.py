

from conan_community_tools.utils.file_view import FileView
from conan_community_tools.templates import render


class BuildPy(FileView):
    name = "build.py"
    language = 'python'

    @staticmethod
    def expected(**context):
        template_name = 'github/build.py'
        return render(template_name, context=context)


if __name__ == "__main__":
    import os
    import logging
    import argparse
    from conan_community_tools.github.api import api_object as g
    from conan_community_tools.github.recipe import Recipe

    parser = argparse.ArgumentParser(description='Run Appveyor example')
    parser.add_argument('--repo', help='Repo name')
    parser.add_argument('--branch', action='append', help='Branches to work over')
    parser.add_argument("-v", "--verbose", dest="verbose_count",
                        action="count", default=0,
                        help="increases log verbosity for each occurence.")
    args = parser.parse_args()

    repo = args.repo or 'conan-community/conan-zlib'
    branches = args.branch or ['release/1.2.11', 'testing/1.2.11', 'release/1.2.8']
    log_level = max(3 - args.verbose_count, 0) * 10

    # Configure logging
    logging.basicConfig(level=log_level)
    logging.getLogger('urllib3').setLevel(level=logging.ERROR)
    logging.getLogger('github').setLevel(level=logging.ERROR)

    g_repo = g.get_repo(repo, lazy=False)
    r = Recipe(g_repo)

    print(f"Recipe: {r}")
    for br in branches:
        print(f" - branch: {br}")
        print(f"\tbuild.py:")
        print("*"*20)
        buildpy = r.get_buildpy_file(branch=br)
        print(buildpy.content)
        print("*"*20)
        print(buildpy.diff().content)
        exit()

