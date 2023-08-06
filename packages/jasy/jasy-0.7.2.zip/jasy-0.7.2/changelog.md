Jasy 0.7.2
==========

- Fix some issues with unused optimizer (SWFObject compilation)
- Added machine ID to verify cache is opened on same machine as created
- Some logging output improvements
- Further improved/fixed GIT support for edge cases
- Added debug logging of detailed shell output (Git only at the moment)


Jasy 0.7.1
==========

- Performance optimizations
- Improved logging output


Jasy 0.7
========

Major
-----

- Completely revamped asset handling. See migration guide for hints on how calls in jasyscript.py need to be modified.
  - Allow modular assets - moved out of kernel.js
  - Improved internal structure of assets for better compression and faster lookup
  - Support for multi profile assets (assets from different locations, roots and with different URL layouts)
  - Support for image sprites and image animations based on configuration files
  - Added information about asset types so that one can access this information on the client via core.io.Asset APIs.
- Added support for generating image sprites from source assets
- Revamped Jasy dependencies to make all dependencies optional (through disabling features). Makes initial installation of Jasy much easier. Added requirements.txt for easy installation of optional packages.
- Added support for omitting repository updates via "--fast"/"-f" option.
- Added help screen when no tasks were given and with "-h" option.

Minor
-----

- Improved categorization of project's content into classes, assets, translations, etc.
- Improved GIT cloning/updating stability.
- Improved output during processing/parsing classes for better user feedback during long runs.
- Renamed formatting=>jsFormatting, optimization=>jsOptimization in preparation of new supported types.
- Added getSortedClasses() to Resolver to omit initializing Sorter() in jasyscript.py at all, making scripts simpler again.
- Improved some edge cases for better error handling. Throwing user friendly JasyError instead of plain Exception.
- Added new utility method getChecksum() to easily detect SHA1 checksum of files.
- Removed typically unused storeCombined() method.


Jasy 0.6.1
==========

- Added `getProjectByName()`, `getGitBranch()`, `sha1File()`, `removeFile()`
- Added possibility to post-register assets using `addFile()`
- Added support for executing Jasy from inside the project structure e.g. from "source/class".
- Improved stability in project handling and git cloning


Jasy 0.6
========

- Major simplification of `jasyscript` via revamp of environment handling
- Support for auto cloning of repositories via `git` (needs system installation)
- Support for project requirements (recursively)
- Revamped console logging (colored and structured)
- Cleanup of project processing/indexing (improved stability/flexibility)
- Support for manually defined project structures to support non-jasy 3rd party projects easily
- Support for calling remote tasks
- Support for executing jasy from a other folder than the project's root


Jasy 0.6-beta2
==============

- Support for project overrides (local project overrides project with same name of any dependency) (useful for hot fixes).


Jasy 0.6-beta1
==============

- Support for checking links, param and return types inside API docs.
- Support API docs for dotted parameters (object parameters with specific required sub keys). 
- Support API doc generation for plain JavaScript statics/members (using namespace={} or namespace.prototype={}) 
- Supporting recursive project dependencies aka project A uses B uses C and A does not know anything about C.
- Improve support for 3rd party JavaScript libraries not matching the Jasy requirements (no jasyproject.conf or matching file layout). This will be implemented moving the configuration and a manual file layout structure into the project requiring this 3rd party library.
- Support for executing and manipulating tasks from other projects e.g. generating build version of project A from project B into a destination folder of project B.
- Added support for automatic and overrideable task prefixes.
- Performance of typical initial `build` tasks was dramatically improved by adding slots and improved deep cloning support to `Node`.


Jasy 0.5
========

- No stable release. Use 0.5-beta12 or 0.6.


Jasy 0.5-beta12
===============

- Added support for validating links inside doc strings
- Added support for validating types in params and return values
- Changed doc output format for param and return types to hold info about linkability, auto-detection, array-like, builtin, pseudo, etc.

Jasy 0.5-beta11
===============

- Added packer script for Mac OS.
- Fixed a few API doc issues.

Jasy 0.5-beta10
===============

- Worked on better API support

Jasy 0.5-beta9
==============

- Improved error handling and output
- Changed format of members/events/properties/statics to sorted arrays
- Apply sorting to uses, implements, etc.

Jasy 0.5-beta8
==============

- Improved markdown handling
- Stabilization when errors happen during API generation 
- Added assets and other meta information to API data

Jasy 0.5-beta7
==============

- Added size calculation of generated files to API data
- Renamed "constructor" key in API data to "construct"
- Minor bug fixes

Jasy 0.5-beta6
==============

- Added cache versioning
- Minor bug fixes

Jasy 0.5-beta5
==============

- Added support for generating a basic search index with all statics/members/properties/events
- Added support for compressing json output
- Added support for ignoring private/internal statics/members
- Added more connections between classes: includedBy and usedBy sections.

Jasy 0.5-beta4
==============

- Added support for merging extensions into destination object (e.g. polyfills, sugar for native objects like String, etc.)
- Added support for generating jsonp output files with custom callback
- Added support for readme.md/package.md package docs

Jasy 0.5-beta3
==============

- Minor fixes

Jasy 0.5-beta2
==============

- Minor fixes for paren optimization

Jasy 0.5-beta1
==============

- Initial release with support for generating API data as JSON/MsgPack files
- Support for generating session based API data with class/interface linking 
- Changed checksum computing to SHA1 to bring it in sync with changes in Core library
- Improved installation process with dependency handling etc.

Jasy 0.4.6
==========

- Minor bug fixes

Jasy 0.4.5
==========

- Minor bug fixes

Jasy 0.4.4
==========

- Minor bug fixes

Jasy 0.4.3
==========

- Minor bug fixes

Jasy 0.4.2
==========

- Minor bug fixes

Jasy 0.4.1
==========

- Minor bug fixes

Jasy 0.4
========

- Restructed to support real installation of Jasy into system folders using easy_install or PIP.
- Changed unit test implementation to Python native library

Jasy 0.3
========

- Initial Release
