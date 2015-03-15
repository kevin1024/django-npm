from ..util import configure_settings
configure_settings()

from npm.finders import get_files

def test_get_files(tmpdir):
    pjson = tmpdir.join('package.json')
    pjson.write('''{
    "name": "test",
    "dependencies": {"mocha": "*"}
    }''')
    get_files(npm_prefix_path=str(tmpdir))

