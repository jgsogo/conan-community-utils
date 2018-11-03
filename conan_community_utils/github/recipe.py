
import os
import re
from github.Repository import Repository

from conan_community_utils import templates
from conan_community_utils.github.conanfile import ConanFile


class Recipe(object):
    """ Models a conan recipe in Github """

    def __init__(self, repo):
        assert isinstance(repo, Repository)
        self._repo = repo

    @classmethod
    def is_recipe(cls, repo_name):
        print(repo_name)
        return bool(re.match(r"conan-[\w_]+", repo_name, re.IGNORECASE))

    @property
    def id(self):
        return str(self._repo.name)

    def __str__(self):
        return self._repo.name

    def __getattr__(self, item):
        """ Fallback to github.Repository properties if not overriden """
        return getattr(self._repo, item)

    @property
    def url(self):
        return "{}.html".format(self._repo.name)

    @property
    def conanfile(self):
        if not hasattr(self, '_conanfile'):
            content = self._repo.get_contents("conanfile.py").decoded_content.decode("utf-8")
            conanfile = ConanFile(content=content)
            setattr(self, '_conanfile', conanfile)
        return getattr(self, '_conanfile')

    @property
    def readme(self):
        content = self._repo.get_contents("README.md").decoded_content.decode("utf-8")
        return {'name': "README.md",
                'content': content,
                'languge': 'markdown'}

    def get_context(self, **context):
        context.update({'recipe': self,
                        'object': self})
        return context

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


if __name__ == "__main__":
    from github import Github

    g = Github(os.getenv("GITHUB_TOKEN"))
    print("Authorized in Github for user '{}'".format(g.get_user().name))

    org = g.get_organization("conan-community").get_repos('all')
    recipes = []
    for r in org[:3]:
        if Recipe.is_recipe(r.name):
            recipes.append(Recipe(repo=r))

    # Testing some outputs
    p = os.path.join(os.path.dirname(__file__), 'tmp')
    os.makedirs(p, exist_ok=True)
    for recipe in recipes:
        filename = recipe.render(output_folder=p, recipe_list=recipes)
        print(filename)

