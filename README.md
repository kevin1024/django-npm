# django-npm [![Build Status](https://travis-ci.org/kevin1024/django-npm.svg?branch=master)](https://travis-ci.org/kevin1024/django-npm)

Want to use npm modules in your django project without vendoring them? django-npm serves as a wrapper around the npm command-line program as well as a staticfiles finder.

## Installation

1. `pip install django-npm`
2. Make sure you have npm installed
3. Make sure you have a `package.json` listing your dependencies
4. If you use a private registry, make sure your `.npmrc` is set up to connect to it
5. Add `npm.finders.NpmFinder` to `STATICFILES_FINDERS`
6. Set some paths in your project's `settings.py`
7. `./manage.py collectstatic`

## Configuration


 * `NPM_ROOT_PATH`: *absolute* path to the npm "root" directory - this is where npm will look for your `package.json`, put your `node_modules` folder and look for a `.npmrc` file
 * `NPM_EXECUTABLE_PATH`: (optional) defaults to wherever `npm` is on your PATH.  If you specify this, you can override the path to the `npm` executable.  This is also an *absolute path*.
 * `NPM_STATIC_FILES_PREFIX`: (optional) Your npm files will end up under this path inside static.  I usually use something like 'js/lib' (so your files will be in /static/js/lib/react.js for example) but you can leave it blank and they will just end up in the root.
 * `NPM_FILE_PATTERNS`: (optional) By default, django-npm will expose all files in `node_modules` to Django as staticfiles.  You may not want *all* of them to be exposed.  You can pick specific files by adding some additional configuration:

    ```python
    NPM_FILE_PATTERNS = {
        'react': ['react.js'],
        'express': ['lib/*.js', 'index.js']
    }
    ```

    Keys are the names of the npm modules, and values are lists containing strings.  The strings match against glob patterns.

## Usage

When you do a `./manage.py collectstatic`, django-npm will run `npm install` for you and copy all the files into your `STATIC_ROOT`.

## Changelog

* v0.1.4 - Fix bug with `NPM_EXECUTABLE_PATH` (thanks @yohanboniface)
* v0.1.3 - Actually fix destination bug
* v0.1.2 - Fix bug with destination prefix
* v0.1.1 - manage.py runserver bugfix
* v0.1.0 - Add `NPM_FILE_PATTERNS` setting
* v0.0.1 - initial release
