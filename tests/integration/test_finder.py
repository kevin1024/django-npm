from ..util import configure_settings
configure_settings()
from django.core.files.storage import FileSystemStorage
from django.test.utils import override_settings

import pytest

from npm.finders import get_files, NpmFinder, npm_install


@pytest.yield_fixture
def npm_dir(tmpdir):
    pjson = tmpdir.join('package.json')
    pjson.write('''{
    "name": "test",
    "dependencies": {"mocha": "*"}
    }''')
    with override_settings(NPM_ROOT_PATH=str(tmpdir)):
        npm_install()
        yield tmpdir


def test_get_files(npm_dir):
    storage = FileSystemStorage(location=str(npm_dir))
    files = get_files(storage, match_patterns='*')
    assert any([True for _ in files])

def test_finder_list_all(npm_dir):
    f = NpmFinder()
    assert any([True for _ in f.list()])

def test_finder_find(npm_dir):
    f = NpmFinder()
    file = f.find('mocha/mocha.js')
    assert file

def test_finder_in_subdirectory(npm_dir):
    with override_settings(NPM_STATIC_FILES_PREFIX='lib'):
        f = NpmFinder()
        assert f.find('lib/mocha/mocha.js')

def test_finder_with_patterns_in_subdirectory(npm_dir):
    with override_settings(NPM_STATIC_FILES_PREFIX='lib', NPM_FILE_PATTERNS={'mocha': ['*']}):
        f = NpmFinder()
        assert f.find('lib/mocha/mocha.js')

def test_no_matching_paths_returns_empty_list(npm_dir):
    with override_settings(NPM_FILE_PATTERNS={'foo': ['bar']}):
        f = NpmFinder()
        assert f.find('mocha/mocha.js') == []
