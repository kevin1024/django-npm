import os
import shlex
import subprocess
from fnmatch import fnmatch

from django.apps import apps
from django.conf import settings
from django.contrib.staticfiles import utils as django_utils
from django.contrib.staticfiles.finders import FileSystemFinder
from django.core.files.storage import FileSystemStorage
from django.utils.six import string_types

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

app = apps.get_app_config("npm")


def npm_install(**config):
    """
    Windows settings
    node_executable = "D:\\Program Files\\nodejs\\node.exe"
    npm_cli = os.path.join(os.path.dirname(node_executable),
                           "node_modules\\npm\\bin\\npm-cli.js")
    :param config: npm_executable
    :return:
    """
    npm_executable = config.setdefault('npm_executable', app.NPM_EXECUTABLE_PATH)

    if isinstance(npm_executable, string_types):
        npm_executable = shlex.split(npm_executable)

    command = npm_executable + ['install', '--prefix=' + app.NPM_ROOT_PATH]

    proc = subprocess.Popen(
        command,
        env={'PATH': os.environ.get('PATH')},
    )
    proc.wait()


def flatten_patterns(patterns):
    if patterns is None:
        return None
    return [
        os.path.join(module, module_pattern)
        for module, module_patterns in patterns.items()
        for module_pattern in module_patterns
    ]


def fnmatch_sub(directory, pattern):
    """
    Match a directory against a potentially longer pattern containing
    wildcards in the path components. fnmatch does the globbing, but there
    appears to be no built-in way to match only the beginning of a pattern.
    """
    length = len(directory.split(os.sep))
    components = pattern.split(os.sep)[:length]
    return fnmatch(directory, os.sep.join(components))


def may_contain_match(directory, patterns):
    return any(fnmatch_sub(directory, pattern) for pattern in patterns)


def get_files(storage, match_patterns='*', ignore_patterns=None, location=''):
    if ignore_patterns is None:
        ignore_patterns = []
    if match_patterns is None:
        match_patterns = []

    directories, files = storage.listdir(location)
    for fn in files:
        if django_utils.matches_patterns(fn, ignore_patterns):
            continue
        if location:
            fn = os.path.join(location, fn)
        if not django_utils.matches_patterns(fn, match_patterns):
            continue
        yield fn
    for dir in directories:
        if django_utils.matches_patterns(dir, ignore_patterns):
            continue
        if location:
            dir = os.path.join(location, dir)
        if may_contain_match(dir, match_patterns) or django_utils.matches_patterns(dir, match_patterns):
            for fn in get_files(storage, match_patterns, ignore_patterns, dir):
                yield fn


class NpmFinder(FileSystemFinder):
    def __init__(self, apps=None, *args, **kwargs):
        self.node_modules_path = app.NPM_ROOT_PATH
        self.destination = getattr(settings, 'NPM_STATIC_FILES_PREFIX', '')
        self.cache_enabled = getattr(settings, 'NPM_FINDER_USE_CACHE', True)
        self.cached_list = None

        self.match_patterns = flatten_patterns(getattr(settings, 'NPM_FILE_PATTERNS', None)) or ['*']
        self.locations = [(self.destination, os.path.join(self.node_modules_path, 'node_modules'))]
        self.storages = OrderedDict()

        filesystem_storage = FileSystemStorage(location=self.locations[0][1])
        filesystem_storage.prefix = self.locations[0][0]
        self.storages[self.locations[0][1]] = filesystem_storage

    def find(self, path, all=False):
        relpath = os.path.relpath(path, self.destination)
        if not django_utils.matches_patterns(relpath, self.match_patterns):
            return []
        return super(NpmFinder, self).find(path, all=all)

    def list(self, ignore_patterns=None):  # TODO should be configurable, add setting
        """List all files in all locations."""
        if self.cache_enabled:
            if self.cached_list is None:
                self.cached_list = list(self._make_list_generator(ignore_patterns))
            return self.cached_list
        return self._make_list_generator(ignore_patterns)

    def _make_list_generator(self, ignore_patterns=None):
        for prefix, root in self.locations:
            storage = self.storages[root]
            for path in get_files(storage, self.match_patterns, ignore_patterns):
                yield path, storage
