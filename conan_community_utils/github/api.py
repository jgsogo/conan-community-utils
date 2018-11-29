
import os
from datetime import datetime, timedelta
import logging
from github import Github

log = logging.getLogger(__name__)


def get_api_object():
    gh = Github(os.getenv("GITHUB_TOKEN"))
    user = gh.get_user()
    log.info(f"Authenticated in Github as user '{user.name}'")
    #log.info(f" - permissions for '{user.login}': {gh.get_user(login=user.login).permissions}")
    return gh

api_object = get_api_object()


def get_rate_limit(raise_at=500):
    global api_object
    rates = api_object.rate_limiting
    reset_in = datetime.fromtimestamp(api_object.rate_limiting_resettime) - datetime.now()
    reset_in = reset_in - timedelta(microseconds=reset_in.microseconds)
    log.debug(f"Rate limit: {rates[0]}/{rates[1]} (reset in {reset_in})")
    if raise_at and rates[0] <= raise_at:
        raise RuntimeError(f"Rate limit under {raise_at}!")
    return rates[0]


if __name__ == '__main__':
    import os
    import argparse

    parser = argparse.ArgumentParser(description='Run Appveyor example')
    #parser.add_argument('--repo', help='Repo name')
    #parser.add_argument('--branch', action='append', help='Branches to work over')
    parser.add_argument("-v", "--verbose", dest="verbose_count",
                        action="count", default=0,
                        help="increases log verbosity for each occurence.")
    args = parser.parse_args()

    #repo = args.repo or 'conan-community/conan-zlib'
    #branches = args.branch or ['release/1.2.11', 'testing/1.2.11', 'release/1.2.8']
    log_level = max(3 - args.verbose_count, 0) * 10

    # Configure login
    logging.basicConfig(level=log_level)
    logging.getLogger('urllib3').setLevel(level=logging.ERROR)
    logging.getLogger('github').setLevel(level=logging.ERROR)

    r = get_rate_limit()
    print(f"Rate limit: {r}")

