
from conan_community_tools.utils.file_view import FileView
from conan_community_tools.templates import render


class AppveyorYML(FileView):
    name = "appveyor.yml"
    language = 'yaml'

    @staticmethod
    def expected(**context):
        template_name = 'github/appveyor.yml'

        # TODO: Define somewhere else:
        global_vars = \
            {
                'conan_username': 'conan',
                'conan_login_username': 'conanbot',
                'conan_channel': 'testing',
                'conan_upload': 'https://api.bintray.com/conan/conan-community/conan',
                #'total_pages': 1,
                #'build_policy': 'missing',
            }

        workers = \
            {
                'Visual Studio 2015':
                    {
                        'version': [12, 14, ],
                        'arch': ['x86', 'x86_64', ],
                        'build_type': ['Release', ],
                        'runtime': ['MT', 'MD', ],
                    },
                'Visual Studio 2017':
                    {
                        'version': [15, ],
                        'arch': ['x86', 'x86_64', ],
                        'build_type': ['Release', ],
                        'runtime': ['MT', 'MD', ],
                    }
            }

        mingw_configurations = [
            "4.9@x86_64@seh@posix",
            "5@x86_64@seh@posix",
            "6@x86_64@seh@posix",
            "7@x86_64@seh@posix"
        ]

        # Explode VS workers
        visual_compilers = []
        for w, items in workers.items():
            for v in items['version']:
                for a in items['arch']:
                    for b in items['build_type']:
                        for r in items['runtime']:
                            visual_compilers.append({
                                'worker_image': w,
                                'version': v,
                                'arch': a,
                                'build_type': b,
                                'runtime': r
                            })

        context = global_vars
        context.update({'visual_compilers': visual_compilers,
                        'mingw_configurations': mingw_configurations})
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
        actual_file = r.get_appveyor_file(branch=br)
        print(actual_file.diff().content)
        exit()


