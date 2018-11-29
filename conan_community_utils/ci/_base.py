
from enum import Enum

import logging
log = logging.getLogger(__name__)


class LastBuildInfo(object):
    class BuildStatus(Enum):
        RUNNING = 0
        UNKNOWN = 1
        SUCCESS = 2
        FAILED = 3

    status = BuildStatus.UNKNOWN
    url = None
    commit = dict.fromkeys(['date', 'message', 'sha'])

    def __str__(self):
        msg_title = self.commit['message'].splitlines()[0]
        return f"{self.status}: {msg_title}"


class CIBase(object):
    def __init__(self, token):
        self._token = token

    def get_last_build(self, repo, branch, *args, **kwargs):
        # TODO: Add checks related to repo and branch
        r = self._get_last_build(repo, branch, *args, **kwargs)
        assert isinstance(r, LastBuildInfo)
        return r

    def _get_last_build(self, repo, branch, *args, **kwargs):
        raise NotImplementedError

    def get_settings(self, repo):
        raise NotImplementedError
