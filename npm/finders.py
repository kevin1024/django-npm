# -*- coding: utf-8 -*-
import fnmatch
import os
import subprocess
from functools import cache, lru_cache
from pathlib import Path

from django.conf import settings
from django.contrib.staticfiles.finders import FileSystemFinder
from django.core.files.storage import FileSystemStorage

NPM_EXECUTABLE_PATH = "NPM_EXECUTABLE_PATH"
NPM_ROOT_PATH = "NPM_ROOT_PATH"
NPM_STATIC_FILES_PREFIX = "NPM_STATIC_FILES_PREFIX"
NPM_FILE_PATTERNS = "NPM_FILE_PATTERNS"
NPM_IGNORE_PATTERNS = "NPM_IGNORE_PATTERNS"
NPM_FINDER_USE_CACHE = "NPM_FINDER_USE_CACHE"


def setting(setting_name, default=None):
    return getattr(settings, setting_name, default)


def npm_install():
    npm = setting(NPM_EXECUTABLE_PATH) or "npm"

    prefix = (
        "--dir"
        if npm.endswith("pnpm")
        else "--cwd"
        if npm.endswith("yarn")
        else "--prefix"
    )

    command = [str(npm), "install", prefix, str(get_npm_root_path())]
    print(" ".join(command))
    proc = subprocess.Popen(
        command,
        env={"PATH": os.environ.get("PATH")},
    )
    return proc.wait()


@cache
def get_npm_root_path():
    return setting(NPM_ROOT_PATH, ".")


def flatten_patterns(patterns):
    if patterns is None:
        return None
    return [
        os.path.join(module, module_pattern)
        for module, module_patterns in patterns.items()
        for module_pattern in module_patterns
    ]


def get_files(
    storage, match_patterns=None, ignore_patterns=None, find_pattern: str | None = None
):
    if match_patterns is None:
        match_patterns = ["*"]
    elif not isinstance(match_patterns, (list, tuple)):
        match_patterns = [match_patterns]

    root = Path(storage.base_location).resolve()

    if not ignore_patterns:
        ignore_patterns = [".*"]

    def splitpath(path: str | Path):
        if path is not None:
            path = str(path)
            p = path.rsplit(os.sep, maxsplit=1)
            return (
                p if len(p) == 2 else (p[0], "*") if path.endswith(os.sep) else ("", p[0])
            )
        return "", ""

    findpath, findname = splitpath(find_pattern)

    @cache
    def ignorelist() -> list:
        return [splitpath(pattern) for pattern in ignore_patterns]

    def ignored(relpath: Path):
        reldir, relname = splitpath(relpath)
        return any(
            fnmatch.fnmatch(relname, ignorefile)
            and (not ignorepath or fnmatch.fnmatch(reldir, ignorepath))
            for (ignorepath, ignorefile) in ignorelist()
        )

    @lru_cache(32767, False)
    def rglob(topdir: Path, pattern: str):
        patternpath, patternname = splitpath(pattern)
        for path in topdir.iterdir():
            relpath = path.relative_to(root)
            if not ignored(relpath):
                # recurse subdirs
                if path.is_dir():
                    yield from rglob(path, pattern)
                elif path.is_file():
                    reldir, relname = splitpath(relpath)
                    # check that the file matches the filename pattern
                    if fnmatch.fnmatch(relname, patternname):
                        if not find_pattern:
                            # if we aren't finding, match on directory part as well
                            if not patternpath or fnmatch.fnmatch(reldir, patternpath):
                                yield relpath
                        # if we are finding, then ensure that the find path matches the relative one
                        elif not findpath or reldir == findpath:
                            # and the name is what we are looking for
                            if fnmatch.fnmatch(relname, findname):
                                yield relpath
        pass

    for match_pattern in match_patterns:
        for path in rglob(root, match_pattern):
            yield path


class NpmFinder(FileSystemFinder):
    # noinspection PyMissingConstructor,PyUnusedLocal
    def __init__(self, *args, **kwargs):
        self.node_modules_path = get_npm_root_path()
        self.destination = setting(NPM_STATIC_FILES_PREFIX, "")
        self.cache_enabled = setting(NPM_FINDER_USE_CACHE, True)
        self.ignore_patterns = setting(NPM_IGNORE_PATTERNS, None) or [".*"]
        self.match_patterns = flatten_patterns(setting(NPM_FILE_PATTERNS, None)) or ["*"]
        self.locations = [
            (self.destination, os.path.join(self.node_modules_path, "node_modules"))
        ]

        filesystem_storage = FileSystemStorage(location=self.locations[0][1])
        filesystem_storage.prefix = self.locations[0][0]
        self.storages = {self.locations[0][1]: filesystem_storage}
        self.cached_list = None

    # noinspection PyShadowingBuiltins
    def find(self, path, all=False):
        relpath = os.path.relpath(path, self.destination)
        for prefix, root in self.locations:
            storage = self.storages[root]
            for p in get_files(
                storage, self.match_patterns, self.ignore_patterns, relpath
            ):
                return root / p
        return []

    def list(self, ignore_patterns=None):
        """List all files in all locations."""
        if not ignore_patterns:
            ignore_patterns = self.ignore_patterns
        elif self.ignore_patterns:
            for pattern in self.ignore_patterns:
                if pattern not in ignore_patterns:
                    ignore_patterns.append(pattern)
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
