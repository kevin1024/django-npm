# -*- coding: utf-8 -*-
from pathlib import Path
from tempfile import TemporaryDirectory
import pytest

from django.core.files.storage import FileSystemStorage
from django.test.utils import override_settings

from npm.finders import get_files, NpmFinder, npm_install
from .util import configure_settings

configure_settings()


# set to npm, pnpm or yarn as desired
# note: pnpm does much better local caching
NPM_EXE = "pnpm"


@pytest.fixture(scope='session')
def setup_npm_dir():
    # don't use py.tmpdir as it is scope='function'
    with TemporaryDirectory() as tmp_path:
        tmp_dir = Path(tmp_path).resolve(strict=True)
        package_json = tmp_dir / 'package.json'
        package_json.write_text('''{
    "name": "test",
    "dependencies": {
        "mocha": "*"
    }
}''')
        with override_settings(NPM_EXECUTABLE_PATH=NPM_EXE, NPM_ROOT_PATH=str(tmp_dir)):
            npm_install()
            yield tmp_dir


@pytest.fixture(scope='function')
def npm_dir(setup_npm_dir):
    tmpdir = setup_npm_dir
    with override_settings(NPM_ROOT_PATH=str(tmpdir)):
        yield tmpdir


@pytest.fixture(scope='function')
def storage(npm_dir):
    return FileSystemStorage(location=str(npm_dir / 'node_modules'))


def test_get_files_all(storage):
    files = list(get_files(storage, match_patterns=['*']))
    assert len(files)
    assert all(filename for filename in files)


def test_get_files_with_patterns(storage):
    files_all = list(get_files(storage, match_patterns=['*.js', '*.css']))
    assert len(files_all)
    assert all(path for path in files_all)
    assert all(Path(path).suffix in ('.js', '.css') for path in files_all)

    files = list(get_files(storage, match_patterns=['mocha/*.js', 'mocha/*.css']))
    assert len(files)
    assert all(path for path in files)
    assert all(Path(path).suffix in ('.js', '.css') for path in files)

    assert files != files_all


def test_finder_list_all(npm_dir):
    f = NpmFinder()
    # using defaults
    results = list(f.list())
    assert len(results)
    assert all(isinstance(result, tuple) for result in results)
    assert all(path for path, storage in results)
    assert all(storage is not None for filename, storage in results)


def test_finder_list_in_module(npm_dir):
    with override_settings(NPM_FILE_PATTERNS={'mocha': ['**/*']}):
        f = NpmFinder()
        # using specific patterns
        results = list(f.list())
        assert len(results)
        assert all(isinstance(result, tuple) for result in results)
        assert all(path for path, storage in results)
        assert all(storage is not None for filename, storage in results)


def test_finder_list_files_in_module(npm_dir):
    with override_settings(NPM_FILE_PATTERNS={'mocha': ['**/*.js', '**/*.css', ]}):
        f = NpmFinder()
        results = list(f.list())
        assert len(results)
        assert all(isinstance(result, tuple) for result in results)
        assert all(path for path, storage in results)
        assert all(storage is not None for filename, storage in results)


def test_finder_find(npm_dir):
    f = NpmFinder()
    file = f.find('mocha/index.js')
    assert file


def test_finder_in_subdirectory(npm_dir):
    with override_settings(NPM_STATIC_FILES_PREFIX='lib',
                           NPM_FILE_PATTERNS={'mocha': ['*']}):
        f = NpmFinder()
        file = f.find('lib/mocha/index.js')
        assert file


def test_finder_with_patterns_in_subdirectory(npm_dir):
    with override_settings(NPM_STATIC_FILES_PREFIX='lib',
                           NPM_FILE_PATTERNS={'mocha': ['*']}):
        f = NpmFinder()
        file = f.find('lib/mocha/index.js')
        assert file


def test_finder_with_patterns_in_directory_component(npm_dir):
    with override_settings(NPM_STATIC_FILES_PREFIX='lib',
                           NPM_FILE_PATTERNS={'mocha': ['*.js']}):
        f = NpmFinder()
        file = f.find('lib/mocha/lib/test.js')
        assert file


def test_no_matching_paths_returns_empty_list(npm_dir):
    with override_settings(NPM_FILE_PATTERNS={'foo': ['bar']}):
        f = NpmFinder()
        result = f.find('mocha/index.js')
        assert result == []


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
