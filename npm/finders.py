import os
import subprocess
from fnmatch import fnmatch
from django.contrib.staticfiles import utils as django_utils
from django.contrib.staticfiles.finders import FileSystemFinder
from django.core.files.storage import FileSystemStorage
from django.conf import settings

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


def npm_install():
    npm_executable_path = getattr(settings, 'NPM_EXECUTABLE_PATH', 'npm')
    npm_prefix_path = getattr(settings, 'NPM_PREFIX_PATH', '.')

def get_node_modules_files(npm_executable_path='npm', npm_prefix_path='.'):
    command = [npm_executable_path, 'install']
    if npm_prefix_path:
        command.append('--prefix=' + npm_prefix_path)
    proc = subprocess.Popen(
        command,
        env={'PATH': os.environ.get('PATH')},
    )
    proc.wait()


def get_files(npm_prefix_path='.'):
    return os.path.join(npm_prefix_path, 'node_modules')


def flatten_patterns(patterns):
    return [
        os.path.join(module, module_pattern)
        for module, module_patterns in patterns.items()
        for module_pattern in module_patterns
    ]


def may_contain_match(directory, patterns):
    return any(pattern.startswith(directory) for pattern in patterns)


def get_files(storage, ignore_patterns=None, match_patterns=None, location=''):
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
            for fn in get_files(storage, ignore_patterns, match_patterns, dir):
                yield fn


class NpmFinder(FileSystemFinder):
    def __init__(self, apps=None, *args, **kwargs):
        files_settings = {}
        if hasattr(settings, 'NPM_EXECUTABLE_PATH'):
            files_settings['npm_executable_path'] = settings.NPM_EXECUTABLE_PATH
        if hasattr(settings, 'NPM_PREFIX_PATH'):
            files_settings['npm_prefix_path'] = settings.NPM_PREFIX_PATH
        files = get_node_modules_files(**files_settings)
        destination = getattr(settings, 'NPM_DESTINATION_PREFIX', '')
        self.locations = [
            (destination, files),
        ]
        self.storages = OrderedDict()

        filesystem_storage = FileSystemStorage(location=self.locations[0][1])
        filesystem_storage.prefix = self.locations[0][0]
        self.storages[self.locations[0][1]] = filesystem_storage

    def find(self, path, all=False):
        patterns = flatten_patterns(getattr(settings, 'NPM_FILE_PATTERNS', None))
        relpath = os.path.relpath(path, getattr(settings, 'NPM_DESTINATION_PREFIX', ''))
        if not django_utils.matches_patterns(patterns, relpath):
            return []
        return super(NpmFinder, self).find(path, all=all)

    def list(self, ignore_patterns):
        """
        List all files in all locations.
        """
        match_patterns = flatten_patterns(getattr(settings, 'NPM_FILE_PATTERNS', None))
        for prefix, root in self.locations:
            storage = self.storages[root]
            for path in get_files(storage, ignore_patterns, match_patterns):
                yield path, storage
