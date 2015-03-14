# django-npm

Want to use npm modules in your django project without vendoring them? django-npm serves as a wrapper around the npm command-line program as well as a staticfiles finder.

## Installation

1. Make sure you have npm installed
2. Make sure you have a `package.json` listing your dependencies
3. If you use a private registry, make sure your `.npmrc` is set up to connect to it
4. Add `npm.finders.NpmFinder` to `STATICFILES_FINDERS`
5. Set some paths in your project's setup.py
6. `./manage.py collectstatic`

## Configuration

 * `NPM_PACKAGE_JSON_PATH`: path to your project's `package.json`
 * `NPM_EXECUTABLE_PATH`: (optional) defaults to wherever `npm` is on your PATH.  If you specify this, you can override the path to the `npm` executable.

## Usage

When you do a `./manage.py collectstatic`, django-npm will run `npm install` for you and copy all the files into your `STATIC_ROOT`.
