# Contributing to ``xfm_tck``
-----------------------------------

> This document is adapted from [https://git.fmrib.ox.ac.uk/fsl/fslpy/-/blob/master/doc/contributing.rst](https://git.fmrib.ox.ac.uk/fsl/fslpy/-/blob/master/doc/contributing.rst)        
> Created by Paul McCarthy

**NOTE**: This document is a work in progress.

Development model
-----------------


* All development occurs on the ``main`` branch.


Commit messages
---------------


To aid readability, all commit messages should be prefixed with one or more of
the following labels (this convention has been inherited from [``nibabel``](https://github.com/nipy/nibabel):

  * *BF*  : bug fix
  * *RF*  : refactoring
  * *ENH*:  enhancement/new feature
  * *BW*  : addresses backward-compatibility
  * *OPT* : optimization
  * *BK*  : breaks something and/or tests fail
  * *PL*  : making pylint happier
  * *DOC* : for all kinds of documentation related commits
  * *TEST*: for adding or changing tests
  * *MNT* : for administrative/maintenance changes
  * *CI*  : for continuous-integration changes


Version number
--------------


The ``xfm_tck`` version number roughly follows [``semantic versioning``](http://semver.org/) rules, so that dependant projects are able to perform
compatibility testing.  The full version number string consists of three
numbers::

    major.minor.patch

- The ``patch`` number is incremented on bugfixes and minor
  (backwards-compatible) changes.

- The ``minor`` number is incremented on feature additions and/or
  backwards-compatible changes.

- The ``major`` number is incremented on major feature additions, and
  backwards-incompatible changes.


The version number in the ``main`` branch should be of the form
``major.minor.patch.dev0``, to indicate that any releases made from this
branch are development releases (although development releases are not part of
the release model).


Releases
--------


A separate branch is created for each **minor** release. The name of the
branch is ``v[major.minor]``, where ``[major.minor]`` is the first two
components of the release version number (see above). For example, the branch
name for minor release ``1.0`` would be ``v1.0``.


Patches and bugfixes may be added to these release branches as ``patch``
releases.  These changes should be made on the main branch like any other
change (i.e. via merge requests), and then cherry-picked onto the relevant
release branch(es).


Every release commit is also tagged with its full version number.  For
example, the first release off the ``v1.0`` branch would be tagged with
``1.0.0``.  Patch releases to the ``v1.0`` branch would be tagged with
``1.0.1``, ``1.0.2``, etc.


### Major/minor releases


Follow this process for major and minor releases. Steps 1 and 2 should be
performed via a merge request onto the main branch, and step 4 via a merge
request onto the relevant minor branch.


1. Update the changelog on the main branch to include the new version number
   and release date.
2. On the main branch, update the version number in ``version.txt`` to
   a development version of **the next** minor release number. For example,
   if you are about to release version ``1.3.0``, the version in the master
   branch should be ``1.4.0.dev0``.
3. Create the new minor release branch off the main branch.
4. Update the version number on the release branch. If CI tests fail on the
   release branch, postpone the release until they are fixed.
5. Tag the new release on the minor release branch.


### Bugfix/patch releases


Follow this process for patch releases. Step 1 should be performed via
a merge request onto the main branch, and step 2 via a merge request onto
the relevant minor branch.


1. Add the fix to the main branch, along with an updated changelog including
   the version number and date for the bugfix release.
2. Cherry-pick the relevant commit(s) from the main branch onto the minor
   release branch, and update the version number on the minor release branch.
   If CI tests fail on the release branch, go back to step 1.
3. Tag the new release on the minor release branch.


Testing
-------


Unit and integration tests are currently run with ``py.test`` and
``coverage`` (**However, this is not yet implemented**).

- Aim for 100% code coverage.
- Tests must pass on python 3.5, 3.6, and 3.7.


Coding conventions
------------------


- Clean, readable code is good
- Clear and accurate documentation is good
- Document all modules, functions, classes, and methods using
  [``ReStructuredText``](http://www.sphinx-doc.org/en/stable/rest.html).

