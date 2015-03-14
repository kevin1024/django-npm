from ..util import configure_settings
configure_settings()

from django.test.utils import override_settings
from npm.finders import NpmFinder

def test_finder(tmpdir):
    pjson = tmpdir.join('package.json')
    pjson.write('''{
    "name": "test",
    "dependencies": {"mocha": "*"}
    }''')
    with override_settings(NPM_PACKAGE_JSON_PATH=str(pjson)):
        f = NpmFinder()
        print list(f.list([]))
