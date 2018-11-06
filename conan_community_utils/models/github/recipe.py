
import os
import re
from github.Repository import Repository as github_Repository

from conan_community_utils.models.travis import Travis
from conan_community_utils.models.appveyor import Appveyor
from conan_community_utils.utils.file_view import FileView
from conan_community_utils.models.github.conanfile import ConanFile


class Readme(FileView):
    name = "README.md"
    language = 'markdown'


class Recipe(object):
    """ Models a conan recipe in Github """

    travis = Travis(token=os.getenv("TRAVIS_TOKEN"))
    appveyor = Appveyor(token=os.getenv("APPVEYOR_TOKEN"))

    def __init__(self, repo):
        assert isinstance(repo, github_Repository)
        self._repo = repo

    def __str__(self):
        return self.id

    @classmethod
    def is_recipe(cls, repo_name):
        return bool(re.match(r"conan-[\w_]+", repo_name, re.IGNORECASE))

    @classmethod
    def is_release_branch(cls, branch_name):
        return bool(re.match(r"release/[a-zA-Z0-9_][a-zA-Z0-9_+.-]+", branch_name))

    @property
    def id(self):
        return str(self._repo.name)

    @property
    def full_name(self):
        return self._repo.full_name

    @property
    def github_url(self):
        return self._repo.html_url  # TODO: git_url

    def get_branches(self):
        return [branch.name for branch in self._repo.get_branches()]

    def get_conanfile(self, branch):
        content = self._repo.get_contents("conanfile.py", ref=branch).decoded_content.decode("utf-8")
        conanfile = ConanFile(content=content)
        return conanfile

    def get_readme(self, branch):
        content = self._repo.get_contents("README.md", ref=branch).decoded_content.decode("utf-8")
        readme = Readme(content=content)
        return readme

    def get_travis_status(self, branch):
        r = self.travis.get_last_build(self.full_name, branch=branch)
        return r.get("state", "unknown")

    def get_appveyor_status(self, branch):
        try:
            r = self.appveyor.get_last_build(repo=self.id, branch=branch)
            return r.get("status", "unknown")
        except AttributeError:
            return "unknown"


    """
    def render(self, output_folder, **context):
        ctxt = self.get_context(**context)

        # detail
        detail_filename = os.path.join(output_folder, self.url)
        templates.render('html/recipe_detail.html', context=ctxt, output_file=detail_filename)

        # conanfile
        conanfile_html = os.path.join(output_folder, self._repo.name + '_conanfile.html')
        ctxt.update({'file': self.conanfile})
        templates.render('html/recipe_detail_file.html', context=ctxt, output_file=conanfile_html)

        # readme
        readme_html = os.path.join(output_folder, self._repo.name + '_readme.html')
        ctxt.update({'file': self.readme})
        templates.render('html/recipe_detail_file.html', context=ctxt, output_file=readme_html)

        return detail_filename
    """


if __name__ == "__main__":
    from github import Github

    g = Github(os.getenv("GITHUB_TOKEN"))

    print("Rate limits")
    print("Calls: {}".format(g.rate_limiting))
    from datetime import datetime
    print("Reset rate: {}".format(datetime.fromtimestamp(g.rate_limiting_resettime)))

    print("Authorized in Github for user '{}'".format(g.get_user().name))

    org = g.get_organization("conan-community").get_repos('all')
    recipes = []
    for r in org[:1]:
        if Recipe.is_recipe(r.name):
            recipes.append(Recipe(repo=r))

    # Testing some outputs
    p = os.path.join(os.path.dirname(__file__), 'tmp')
    os.makedirs(p, exist_ok=True)
    for recipe in recipes:
        #filename = recipe.render(output_folder=p, recipe_list=recipes)
        #print(filename)
        print(recipe)
        print(recipe._repo.html_url)
        for branch in recipe.get_branches():
            print(" - {} is release {}".format(branch, Recipe.is_release_branch(branch)))
            if Recipe.is_release_branch(branch):
                conanfile = recipe.get_conanfile(branch=branch)
                print(conanfile._attribs["version"])
                print(recipe.get_travis_status(branch=branch))
                print(recipe.get_appveyor_status(branch=branch))

    print("Rate limits")
    print("Calls: {}".format(g.rate_limiting))
    from datetime import datetime
    print("Reset rate: {}".format(datetime.fromtimestamp(g.rate_limiting_resettime)))