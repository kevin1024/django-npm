from __future__ import print_function

import os
import shlex
import subprocess
import sys
from fnmatch import fnmatch
from logging import getLogger

from django.contrib.staticfiles import utils as django_utils
from django.contrib.staticfiles.finders import FileSystemFinder
from django.core.files.storage import FileSystemStorage

from npm.compat import OrderedDict
from npm.conf import settings
from npm.process import StdinWriter

logger = getLogger(__name__)


def npm_install(**config):
    """Install nodejs packages"""
    npm_executable = config.setdefault('npm_executable', settings.NPM_EXECUTABLE_PATH)
    npm_workdir = config.setdefault('npm_workdir', settings.NPM_ROOT_PATH)
    npm_command_args = config.setdefault('npm_command_args', ())

    command = shlex.split(npm_executable)

    if not npm_command_args:
        command.extend(['install', '--prefix=' + settings.NPM_ROOT_PATH])
    else:
        command.extend(npm_command_args)

    proc = subprocess.Popen(
        command,
        env=os.environ,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=subprocess.PIPE,
        universal_newlines=True,
        cwd=npm_workdir,
        bufsize=2048
    )
    with StdinWriter(proc):
        try:
            while proc.poll() is None:
                data = proc.stdout.read(1)
                if not data:
                    break
                print(data, file=sys.stdout, end='')
        finally:
            proc.stdout.close()

    logger.debug("%s %s" % (proc.poll(), command))
    # npm code
    return proc.poll()


def flatten_patterns(patterns):
    if patterns is None:
        return None
    return [
        os.path.normpath(os.path.join(module, module_pattern))
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
        self.node_modules_path = settings.NPM_ROOT_PATH
        self.destination = settings.NPM_STATIC_FILES_PREFIX
        self.cache_enabled = settings.NPM_FINDER_USE_CACHE
        self.cached_list = None

        self.match_patterns = flatten_patterns(settings.NPM_FILE_PATTERNS) or ['*']
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
            if not os.path.exists(root):
                continue
            storage = self.storages[root]
            for path in get_files(storage, self.match_patterns, ignore_patterns):
                yield path, storage
