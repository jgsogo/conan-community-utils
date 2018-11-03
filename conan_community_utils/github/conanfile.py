
import ast


class MyVisitor(ast.NodeVisitor):
    conanfile_attribs = {}

    def visit_ClassDef(self, node):
        # Identify the Recipe one
        bases = [it.id for it in node.bases]
        if 'ConanFile' not in bases:
            return

        for statement in node.body:
            if isinstance(statement, ast.Assign):
                if len(statement.targets) == 1 and isinstance(statement.targets[0], ast.Name):

                    def get_value(value):
                        if isinstance(value, ast.Str):
                            return value.s
                        elif isinstance(value, ast.Tuple):
                            return [it.s for it in value.elts]
                        elif isinstance(value, ast.List):
                            return [get_value(it) for it in value.elts]
                        elif isinstance(value, ast.Dict):
                            return {k.s: get_value(v) for k, v in zip(value.keys, value.values)}
                        elif isinstance(value, ast.NameConstant):
                            return value.value
                        else:
                            #print(type(value))
                            #print(vars(value))
                            pass

                    self.conanfile_attribs[str(statement.targets[0].id)] = get_value(statement.value)


class ConanFile(object):
    name = 'conanfile.py'
    language = 'python'

    def __init__(self, content):
        self._content = content

        root = ast.parse(self._content)
        visitor = MyVisitor()
        visitor.visit(root)
        self._attribs = visitor.conanfile_attribs

    def __getattr__(self, item):
        return self._attribs.get(item)

    @property
    def content(self):
        return self._content


if __name__ == '__main__':
    conanfile = """
from conans import ConanFile, tools, CMake, AutoToolsBuildEnvironment
from conans.util import files
import os
 
 
class ZlibConan(ConanFile):
    name = "zlib"
    version = "1.2.11"
    ZIP_FOLDER_NAME = "zlib-%s" % version
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    exports_sources = ["CMakeLists.txt"]
    url = "http://github.com/lasote/conan-zlib"
    license = "Zlib"
    description = "A Massively Spiffy Yet Delicately Unobtrusive Compression Library " \
                  "(Also Free, Not to Mention Unencumbered by Patents)"

    """

    c = ConanFile(content=conanfile)
