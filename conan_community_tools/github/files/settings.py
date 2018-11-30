
from conan_community_tools.utils.file_view import FileView
from conan_community_tools.templates import render


class SettingsYML(FileView):
    name = "settings.yml"
    language = 'yaml'

    @staticmethod
    def expected(**context):
        template_name = 'github/settings.yml'
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

    settings_ctxt = {'topics': ', '.join(r.get_topics()),
                     'description': r.description,
                     'homepage': r.homepage}

    print(f"Recipe: {r}")
    print(f"\t.settings.py:")
    actual_file = r.get_github_settings_file()
    if actual_file:
        print(actual_file.expected(**settings_ctxt))
        #print(actual_file.diff().content)
        exit()
    else:
        print("expected")
        print(SettingsYML("").expected(**settings_ctxt))
        print("Not found")
