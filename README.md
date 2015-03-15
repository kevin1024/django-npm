# django-npm

Want to use npm modules in your django project without vendoring them? django-npm serves as a wrapper around the npm command-line program as well as a staticfiles finder.

## Installation

1. `pip install django-npm`
2. Make sure you have npm installed
3. Make sure you have a `package.json` listing your dependencies
4. If you use a private registry, make sure your `.npmrc` is set up to connect to it
5. Add `npm.finders.NpmFinder` to `STATICFILES_FINDERS`
6. Set some paths in your project's setup.py
7. `./manage.py collectstatic`

## Configuration

Note: all paths must be *absolute* paths.

 * `NPM_PREFIX_PATH`: Path to the npm "prefix' directory - this is where npm will look for your `package.json`, put your `node_modules` folder and look for a `.npmrc` file
 * `NPM_EXECUTABLE_PATH`: (optional) defaults to wherever `npm` is on your PATH.  If you specify this, you can override the path to the `npm` executable.
 * `NPM_DESTINATION_PATH`: (optional) Your npm files will end up under this directory.  I usually use something like 'js/lib' but you can leave it blank and they will just end up in the root.

## Usage

When you do a `./manage.py collectstatic`, django-npm will run `npm install` for you and copy all the files into your `STATIC_ROOT`.
