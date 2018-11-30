
import difflib


class FileView(object):
    name = None
    language = None

    def __init__(self, content):
        self.content = content

    @staticmethod
    def expected(**context):
        raise NotImplementedError

    def diff(self, **context):
        expected_content = self.expected(**context)
        lines = difflib.unified_diff(self.content.splitlines(), expected_content.splitlines(),
                                     fromfile='actual', tofile='expected', lineterm='', n=3)
        return DiffFile(name=self.name, content='\n'.join(lines))


class DiffFile(FileView):
    language = 'diff'

    def __init__(self, name, content):
        super().__init__(content=content)
        self.name = name