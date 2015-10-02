from ..util import configure_settings
configure_settings()
from django.test.utils import override_settings
import pytest

from npm.finders import get_files, NpmFinder

@pytest.yield_fixture
def npm_dir(tmpdir):
    pjson = tmpdir.join('package.json')
    pjson.write('''{
    "name": "test",
    "dependencies": {"mocha": "*"}
    }''')
    with override_settings(NPM_PREFIX_PATH=str(tmpdir)):
        yield tmpdir


def test_get_files(npm_dir):
    get_files(npm_prefix_path=str(npm_dir))

def test_finder_list(npm_dir):
    f = NpmFinder()
    assert len(f.list([]))

def test_finder_find(npm_dir):
    f = NpmFinder()
    assert f.find('mocha/mocha.js')

def test_finder_in_subdirectory(npm_dir):
    with override_settings(NPM_DESTINATION_PREFIX='lib'):
        f = NpmFinder()
        assert f.find('lib/mocha/mocha.js')

def test_no_matching_paths_returns_empty_list(npm_dir):
    f = NpmFinder()
    with override_settings(NPM_FILE_PATTERNS={'foo':['bar']}):
        assert f.find('mocha/mocha.js') == []
