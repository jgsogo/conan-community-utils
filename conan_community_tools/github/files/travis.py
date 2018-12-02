
from conan_community_tools.utils.file_view import FileView
from conan_community_tools.templates import render


class TravisYML(FileView):
    name = ".travis.yml"
    language = 'yaml'

    @staticmethod
    def expected(config, **context):
        template_name = 'github/.travis.yml'

        gcc_compilers = []
        for gcc_compiler in config['travis']['gcc_compilers']:
            for v in gcc_compiler['versions']:
                gcc_compilers.append({'docker': gcc_compiler['docker'], 'version': v})

        clang_compilers = []
        for clang_compiler in config['travis']['clang_compilers']:
            for v in clang_compiler['versions']:
                clang_compilers.append({'docker': clang_compiler['docker'], 'version': v})

        apple_clang_compilers = []
        for apple_clang_compiler in config['travis']['apple_clang_compilers']:
            for v in apple_clang_compiler['versions']:
                apple_clang_compilers.append({'osx_image': apple_clang_compiler['osx_image'], 'version': v})

        context.update({'gcc_compilers': gcc_compilers,
                        'clang_compilers': clang_compilers,
                        'apple_clang_compilers': apple_clang_compilers,
                        'config': config})
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
        actual_file = r.get_travis_file(branch=br)
        print(actual_file.expected())
        #print(actual_file.diff().content)
        exit()
