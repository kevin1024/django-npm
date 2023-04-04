# -*- coding: utf-8 -*-
import os
import subprocess
from pathlib import Path

from django.contrib.staticfiles import utils as django_utils
from django.contrib.staticfiles.finders import FileSystemFinder
from django.core.files.storage import FileSystemStorage
from django.conf import settings


def setting(setting_name, default=None):
    return getattr(settings, setting_name, default)


def npm_install():
    npm = setting('NPM_EXECUTABLE_PATH')
    yarn = setting('YARN_EXECUTABLE_PATH')
    pnpm = setting('PNPM_EXECUTABLE_PATH')

    prefix = '--prefix'
    if pnpm:
        npm = pnpm or "pnpm"
        prefix = '--dir'
    elif yarn:
        npm = yarn or "yarn"
        prefix = '--cwd'
    elif npm is None:
        npm = npm or 'npm'

    command = [str(npm), 'install', prefix, str(get_npm_root_path())]
    print(" ".join(command))
    proc = subprocess.Popen(command, env={'PATH': os.environ.get('PATH')},)
    return proc.wait()


def get_npm_root_path():
    return setting('NPM_ROOT_PATH', '.')


def flatten_patterns(patterns):
    if patterns is None:
        return None
    return [
        os.path.join(module, module_pattern)
        for module, module_patterns in patterns.items()
        for module_pattern in module_patterns
    ]


def get_files(storage, match_patterns=None, ignore_patterns=None):
    if match_patterns is None:
        match_patterns = ['*']

    root = Path(storage.base_location).resolve()
    ignore_paths = []
    if ignore_patterns:
        for ignore_pattern in ignore_patterns:
            for ignore_path in root.glob(ignore_pattern):
                ignore_paths.append(ignore_path.relative_to(root))
    for match_pattern in match_patterns:
        # let Path.glob do all the work
        for path in root.glob(match_pattern):
            if path.is_file():
                path = path.relative_to(root)
                if path not in ignore_paths:
                    yield path


class NpmFinder(FileSystemFinder):
    # noinspection PyMissingConstructor,PyUnusedLocal
    def __init__(self, *args, **kwargs):
        self.node_modules_path = get_npm_root_path()
        self.destination = setting('NPM_STATIC_FILES_PREFIX', '')
        self.cache_enabled = setting('NPM_FINDER_USE_CACHE', True)

        self.match_patterns = flatten_patterns(setting('NPM_FILE_PATTERNS', None)) or ['*']
        self.locations = [(self.destination, os.path.join(self.node_modules_path, 'node_modules'))]

        filesystem_storage = FileSystemStorage(location=self.locations[0][1])
        filesystem_storage.prefix = self.locations[0][0]
        self.storages = {self.locations[0][1]: filesystem_storage}
        self.cached_list = None

    # noinspection PyShadowingBuiltins
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
