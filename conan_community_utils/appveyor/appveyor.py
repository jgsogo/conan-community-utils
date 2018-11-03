
from appveyor_client import AppveyorClient

from .project import Project
from .role import Role


class AppVeyor(object):
    def __init__(self, appveyor_token):
        self._appveyor = AppveyorClient(appveyor_token)

    def __str__(self):
        return self.username

    def get_roles(self):
        for it in self._appveyor.roles.get():
            yield Role(it, self._appveyor)

    def get_projects(self):
        for it in self._appveyor.projects.get():
            yield Project(it, self._appveyor)


if __name__ == "__main__":
    import os
    from pprint import pprint

    t = AppVeyor(os.getenv("APPVEYOR_TOKEN"))
    print("Roles:")
    for it in t.get_roles():
        print("\t- {}".format(it))

    print("Projects:")
    for it in t.get_projects():
        print("\t- {}".format(it))
        print(it.get_status(branch="feauture/profile_auto"))

