import tempfile
import shutil
import os
import subprocess
import collections
from django.contrib.staticfiles.finders import FileSystemFinder
from django.core.files.storage import FileSystemStorage
from django.conf import settings

def get_files(package_json_path, npm_executable_path, npm_config_file_path=None):
    dir_path = tempfile.mkdtemp()
    shutil.copy(package_json_path, dir_path)
    shutil.copy(npm_config_file_path, dir_path)
    proc = subprocess.Popen(
        ['npm' or npm_executable_path, 'install'],
        env={'PATH': os.environ.get('PATH')},
        cwd=dir_path,
    )
    proc.wait()
    return os.path.join(dir_path, 'node_modules')


class NpmFinder(FileSystemFinder):
    def __init__(self, apps=None, *args, **kwargs):
        files = get_files(
            settings.NPM_PACKAGE_JSON_PATH, 
            getattr(settings, 'NPM_EXECUTABLE_PATH', None),
            getattr(settings, NPM_CONFIG_FILE_PATH, None),
        )
        self.locations = [
            ('', files),
        ]
        self.storages = collections.OrderedDict()

        filesystem_storage = FileSystemStorage(location=self.locations[0][1])
        filesystem_storage.prefix = self.locations[0][0]
        self.storages[self.locations[0][1]] = filesystem_storage
