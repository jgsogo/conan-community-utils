

class Project(object):
    def __init__(self, data, appveyor):
        self._appveyor = appveyor
        self._data = data

    def __str__(self):
        return self.name

    def __getattr__(self, item):
        return self._data.get(item)

    def get_status(self, branch):
        data = self._appveyor.projects.last_branch_build(account_name=self.accountName,
                                                         project_slug=self.slug,
                                                         build_branch=branch)
        return data["build"]["status"]
