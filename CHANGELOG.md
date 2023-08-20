# Changelog
# v1.4.0
- add pre-commit checks for quality improvement
- add a "test" dependency group and move pytest there
- revoke more python versions (now >= 3.10) due to use of PEP604 annotation syntax
# v1.3.0
- don't use pnpm by default, esp for testing when not available
# v1.2.0
- drop support for Python versions that contemporary Django no longer support
- add pnpm support
# v1.1.3
- Fix get_files to return relative paths
# v1.0.1
- Convert build to use poetry
- Use pathlib with glob matching instead of fnmatch for more flexibility
# v1.0.0
- Improve speed, separate `npm install` from the finder
# v0.1.4
- Fix bug with `NPM_EXECUTABLE_PATH` (thanks @yohanboniface)
# v0.1.3
- Actually fix destination bug
# v0.1.2
- Fix bug with destination prefix
# v0.1.1
- manage.py runserver bugfix
# v0.1.0
- Add `NPM_FILE_PATTERNS` setting
# v0.0.1
- initial release
