from django.conf import settings

settings.configure(DEBUG=True)

from npm.finders import get_files

def test_get_files(tmpdir):
    pjson = tmpdir.join('package.json')
    pjson.write('''{
    "name": "test",
    "dependencies": {"mocha": "*"}
    }''')
    get_files(npm_prefix_path=str(tmpdir))

