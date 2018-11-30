
from conan_community_utils.utils.file_view import FileView
from conan_community_utils.templates import render


class TravisYML(FileView):
    name = ".travis.yml"
    language = 'yaml'

    @staticmethod
    def expected(**context):
        template_name = 'github/.travis.yml'

        # TODO: Define somewhere else:
        global_vars = \
            {
                'conan_username': 'conan',
                'conan_login_username': 'conanbot',
                'conan_channel': 'testing',
                'conan_upload': 'https://api.bintray.com/conan/conan-community/conan',
                # 'total_pages': 1,
                # 'build_policy': 'missing',
            }

        def get_compilers(tuples, version='version', docker_image='docker_image'):
            ret = []
            for v, di in tuples:
                ret.append({version: v, docker_image: di})
            return ret

        gcc_compilers = get_compilers([
            (4.8, 'conanio/gcc48'),
            (4.9, 'conanio/gcc49'),
            (5, 'conanio/gcc5'),
            (6, 'conanio/gcc6'),
            (7, 'conanio/gcc7'),
            (8, 'conanio/gcc8')
        ])

        clang_compilers = get_compilers([
            (3.9, 'conanio/clang39'),
            (4.0, 'conanio/clang40'),
            (5.0, 'conanio/clang50'),
            (6.0, 'conanio/clang60'),
            (7.0, 'conanio/clang7'),
        ])

        apple_clang_compilers = get_compilers(version='version', docker_image='osx_image', tuples=[
            (7.3, 'xcode7.3'),
            (8.1, 'xcode8.1'),
            (9.0, 'xcode9.0'),
            (9.1, 'xcode9.1'),
            (10.0, 'xcode10.0'),
        ])

        context = global_vars
        context.update({'gcc_compilers': gcc_compilers,
                        'clang_compilers': clang_compilers,
                        'apple_clang_compilers': apple_clang_compilers})
        return render(template_name, context=context)


if __name__ == "__main__":
    import os
    import logging
    import argparse
    from conan_community_utils.github.api import api_object as g
    from conan_community_utils.github.recipe import Recipe

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
