import os
import sys
import subprocess
import pkg_resources
from xml.etree.ElementTree import fromstring

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


def which(program):
    # adapted from <http://stackoverflow.com/questions/377017>
    path, name = os.path.split(program)
    for path in ['.'] + os.environ['PATH'].split(os.pathsep):
        filename = os.path.join(path, program)
        if os.path.exists(filename) and os.access(filename, os.X_OK):
            return filename


class JSHintTestGenerator(type):

    def __new__(cls, name, bases, dict):
        for filename in cls._collect_files(
            dict.get('include', ()), dict.get('exclude', ())):
            cls._create_runner(dict, filename)
        return type.__new__(cls, name, bases, dict)

    @classmethod
    def _create_runner(cls, dict, filename):
        name = 'test_%s' % os.path.basename(filename)
        name = cls._uniquify_name(dict, name)
        dict[name] = lambda x: x._run(filename)

    @classmethod
    def _uniquify_name(cls, dict, name):
        if name not in dict:
            return name
        base = name
        counter = 1
        while name in dict:
            name = '%s_%s' % (base, counter)
            if name not in dict:
                return name
            counter += 1

    @classmethod
    def _collect_files(cls, include, exclude):
        files = []
        for path in include:
            package, path = path.split(':', 1)
            for filename in pkg_resources.resource_listdir(package, path):
                basename, extension = os.path.splitext(filename)
                if extension.lower() != '.js':
                    continue
                files.append(pkg_resources.resource_filename(
                        package, os.path.join(path, filename)))

        result = []
        for path in files:
            basename = os.path.basename(path)
            if basename not in exclude:
                result.append(path)
        return result


class JSHintTestCase(unittest.TestCase):

    __metaclass__ = JSHintTestGenerator

    jshint_command = 'jshint'
    include = tuple()
    exclude = tuple()
    options = tuple()
    ignore = tuple()

    def __init__(self, *args, **kw):
        super(JSHintTestCase, self).__init__(*args, **kw)
        self._command = which(os.environ.get(
                'UNITTEST_JSHINT_COMMAND', self.jshint_command))

    def _run(self, filename):
        if not self._command:
            raise unittest.SkipTest('%r not found on $PATH' % self._command)

        job = subprocess.Popen([self._command] + list(self.options) + \
                [filename, '--jslint-reporter'], stdout=subprocess.PIPE)
        job.wait()
        output = job.communicate()[0]

        tree = fromstring(output)
        cwdpath, errors = os.getcwd().split('/'), []
        for _file in tree.findall('file'):
            for _issue in _file.findall('issue'):
                filepath = _file.get('name').split('/')
                for i, itempath in enumerate(filepath):
                    if i < len(cwdpath) and cwdpath[i] == itempath:
                        continue
                    filename = '/'.join(filepath[i:])
                    break
                errors.append('%s: line %s, col %s, %s' % (
                    filename,
                    _issue.get('line'),
                    _issue.get('char'),
                    _issue.get('reason'),
                    ))
        if errors:
            self.fail('JSHint Errors\n' + '\n'.join(errors))
