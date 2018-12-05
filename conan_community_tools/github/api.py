
import os
from datetime import datetime, timedelta
import logging
from github import Github

from conan_community_tools.environment import GITHUB_TOKEN

log = logging.getLogger(__name__)


def get_client():
    token = os.getenv(GITHUB_TOKEN)
    if not token:
        raise EnvironmentError(f"Provide env variable '{GITHUB_TOKEN}'")

    gh = Github(token)
    return gh


def get_rate_limit(client, raise_at=500):
    rates = client.rate_limiting
    reset_in = datetime.fromtimestamp(client.rate_limiting_resettime) - datetime.now()
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

