
from conan_community_tools.utils.file_view import FileView
from conan_community_tools.templates import render
from conan_community_tools.ci._base import LastBuildInfo


def travis_badge(status):
    f"https://travis-ci.org/bincrafters/conan-libpq.svg?branch=stable%2F9.6.9"
    assert isinstance(status, LastBuildInfo.BuildStatus), type(status)
    if status == LastBuildInfo.BuildStatus.SUCCESS:
        return "success"
    else:
        raise NotImplementedError(f"Unknown status: {status}")


def appveyor_badge(status):
    assert isinstance(status, LastBuildInfo.BuildStatus), type(status)
    if status == LastBuildInfo.BuildStatus.SUCCESS:
        return "success"
    else:
        raise NotImplementedError(f"Unknown status: {status}")


class Readme(FileView):
    name = "README.md"
    language = 'markdown'

    @staticmethod
    def expected(**context):
        template_name = 'github/README.md'
        #context.update({'recipe': recipe, 'branch': branch})
        add_globals = {'travis_badge': travis_badge, 'appveyor_badge': appveyor_badge}
        return render(template_name, context=context, add_globals=add_globals)


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

    g_repo = g.get_repo(repo, lazy=False)
    r = Recipe(g_repo)

    print(f"Recipe: {r}")
    for br in branches:
        print(f" - branch: {br}")
        print(f"\tREADME.md:")
        actual_file = r.get_readme_file(branch=br)
        print(actual_file.expected(recipe=r, branch=br))
        #print(actual_file.diff().content)
        exit()
