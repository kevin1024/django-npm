# django-npm [![Build Status](https://travis-ci.org/kevin1024/django-npm.svg?branch=master)](https://travis-ci.org/kevin1024/django-npm)

Want to use npm modules in your django project without vendoring them? django-npm serves as a wrapper around the npm command-line program as well as a staticfiles finder.

## Installation

1. `$ pip install django-npm`
2. Install npm. If you use a private registry, make sure your `.npmrc` is set up to connect to it
3. Have a `package.json` at the root of your project, listing your dependencies
4. Add `npm.finders.NpmFinder` to `STATICFILES_FINDERS`
5. Configure your `settings.py`
6. `$ npm install` with the command line, or with Python: `from npm.finders import npm_install; npm_install()`
7. `$ ./manage.py collectstatic` will copy all selected node_modules files into your `STATIC_ROOT`.

## Configuration

 * `NPM_ROOT_PATH`: *absolute* path to the npm "root" directory - this is where npm will look for your `package.json`, put your `node_modules` folder and look for a `.npmrc` file
 * `NPM_EXECUTABLE_PATH`: (optional) defaults to wherever `npm` is on your PATH.  If you specify this, you can override the path to the `npm` executable.  This is also an *absolute path*.
 * `NPM_STATIC_FILES_PREFIX`: (optional) Your npm files will end up under this path inside static.  I usually use something like ` os.path.join('js', 'lib')` (so your files will be in /static/js/lib/react.js for example) but you can leave it blank and they will just end up in the root.
 * `NPM_FILE_PATTERNS`: (optional) By default, django-npm will expose all files in `node_modules` to Django as staticfiles.  You may not want *all* of them to be exposed.  You can pick specific files by adding some additional configuration:

    ```python
    NPM_FILE_PATTERNS = {
        'react': ['react.js'],
        'express': ['lib/*.js', 'index.js']
    }
    ```

    Keys are the names of the npm modules, and values are lists containing strings.  The strings match against glob patterns.

 * `NPM_FINDER_USE_CACHE`: (default True) A boolean that enables cache in the finder. If enabled, the file list will be computed only once, when the server is started.

## npm install

If you want to run `npm install` programmatically, you can do:

```python
from npm.finders import npm_install
npm_install()
```

## Changelog

* v1.0.0 - Improve speed, separate `npm install` from the finder
* v0.1.4 - Fix bug with `NPM_EXECUTABLE_PATH` (thanks @yohanboniface)
* v0.1.3 - Actually fix destination bug
* v0.1.2 - Fix bug with destination prefix
* v0.1.1 - manage.py runserver bugfix
* v0.1.0 - Add `NPM_FILE_PATTERNS` setting
* v0.0.1 - initial release
