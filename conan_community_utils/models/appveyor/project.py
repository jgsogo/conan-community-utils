

class Project(object):
    def __init__(self, data, appveyor):
        self._appveyor = appveyor
        self._data = data

    def __str__(self):
        return self.name

    @property
    def appveyor_url(self):
        return "https://ci.appveyor.com/{}".format(self._data[""])

    @property
    def full_name(self):
        return self._data["repositoryName"]

    def get_status(self, branch):
        data = self._appveyor.projects.last_branch_build(account_name=self.accountName,
                                                         project_slug=self.slug,
                                                         build_branch=branch)
        return data["build"]["status"]
