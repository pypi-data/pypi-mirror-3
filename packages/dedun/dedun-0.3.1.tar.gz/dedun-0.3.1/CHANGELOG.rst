Changelog
*********

0.3.1
=====

- Added versiontools >= 1.8 setup requirement.

0.3.0
=====

- Fixed issue #1: Slicing does not respect reverse() method.
- Added new method ResultBase.get_json.
- Added test suite (using py.test).
- Reorganized code as a Python package.
- Using BSD license now.
- Requires now anyjson >= 0.3.1.

0.2.5
=====

- Added new Results methods order_by and reverse.

0.2.4
=====

- Fixed installation instructions.

0.2.3
=====

- Fixed setup.py encodings (again).

0.2.2
=====

- Fixed setup.py encodings.

0.2.1
=====

- Minor fixes.

0.2.0
=====

- New Resource and Result classes.
- Added debug argument to Resource classes.
- New ObjectNotFound, ImproperlyConfigured and MultipleResults exceptions.

0.1.0
=====

- Initial release. Supports only JSON. Documentation and tests will come with
  future releases.
