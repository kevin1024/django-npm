# -*- coding: utf-8 -*-
from pathlib import Path
from tempfile import TemporaryDirectory

from .util import configure_settings
configure_settings()

import pytest

from django.core.files.storage import FileSystemStorage
from django.test.utils import override_settings

from npm.finders import get_files, NpmFinder, npm_install


@pytest.fixture(scope='session')
def setup_npm_dir():
    # don't use py.tmpdir as it is scope='function'
    with TemporaryDirectory() as tmppath:
        tmpdir = Path(tmppath).resolve(strict=True)
        package_json = tmpdir / 'package.json'
        package_json.write_text('''{
    "name": "test",
    "dependencies": {"mocha": "*"}
}''')
        with override_settings(NPM_ROOT_PATH=str(tmpdir)):
            npm_install()
            yield tmpdir


@pytest.fixture(scope='function')
def npm_dir(setup_npm_dir):
    tmpdir = setup_npm_dir
    with override_settings(NPM_ROOT_PATH=str(tmpdir)):
        yield tmpdir


@pytest.fixture(scope='function')
def storage(npm_dir):
    return FileSystemStorage(location=str(npm_dir / 'node_modules'))


def test_get_files_all(storage):
    files = list(get_files(storage, match_patterns='*'))
    assert len(files)
    assert all(filename for filename in files)


def test_get_files_with_patterns(storage):
    files_all = list(get_files(storage, match_patterns=['**/*.js', '**/*.css']))
    assert len(files_all)
    assert all(path for path in files_all)
    assert all(Path(path).suffix in ('.js', '.css') for path in files_all)

    files = list(get_files(storage, match_patterns=['*/*.js', '*/*.css']))
    assert len(files)
    assert all(path for path in files)
    assert all(Path(path).suffix in ('.js', '.css') for path in files_all)

    assert files != files_all


def test_finder_list_all(npm_dir):
    f = NpmFinder()
    results = list(f.list())
    assert len(results)
    assert all(isinstance(result, tuple) for result in results)
    assert all(path for path, storage in results)
    assert all(storage is not None for filename, storage in results)


def test_finder_list_in_module(npm_dir):
    with override_settings(NPM_FILE_PATTERNS={'mocha': ['*']}):
        f = NpmFinder()
        results = list(f.list())
        assert len(results)
        assert all(isinstance(result, tuple) for result in results)
        assert all(path for path, storage in results)
        assert all(storage is not None for filename, storage in results)


def test_finder_list_files_in_module(npm_dir):
    with override_settings(NPM_FILE_PATTERNS={'mocha': ['*.js','*.css',]}):
        f = NpmFinder()
        results = list(f.list())
        assert len(results)
        assert all(isinstance(result, tuple) for result in results)
        assert all(path for path, storage in results)
        assert all(storage is not None for filename, storage in results)


def test_finder_find(npm_dir):
    f = NpmFinder()
    file = f.find('mocha/mocha.js')
    assert file


def test_finder_in_subdirectory(npm_dir):
    with override_settings(NPM_STATIC_FILES_PREFIX='lib'):
        f = NpmFinder()
        assert f.find('lib/mocha/mocha.js')


def test_finder_with_patterns_in_subdirectory(npm_dir):
    with override_settings(NPM_STATIC_FILES_PREFIX='lib',
                           NPM_FILE_PATTERNS={'mocha': ['*']}):
        f = NpmFinder()
        assert f.find('lib/mocha/mocha.js')


def test_finder_with_patterns_in_directory_component(npm_dir):
    with override_settings(NPM_STATIC_FILES_PREFIX='lib',
                           NPM_FILE_PATTERNS={'mocha': ['*/*js']}):
        f = NpmFinder()
        assert f.find('lib/mocha/lib/test.js')


def test_no_matching_paths_returns_empty_list(npm_dir):
    with override_settings(NPM_FILE_PATTERNS={'foo': ['bar']}):
        f = NpmFinder()
        assert f.find('mocha/mocha.js') == []


def test_finder_cache(npm_dir):
    with override_settings(NPM_FINDER_USE_CACHE=True):
        f = NpmFinder()
        f.list()
        assert f.cached_list is not None
        assert f.list() is f.cached_list


def test_finder_no_cache(npm_dir):
    with override_settings(NPM_FINDER_USE_CACHE=False):
        f = NpmFinder()
        f.list()
        assert f.cached_list is None
        assert f.list() is not f.cached_list
