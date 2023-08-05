#!/usr/bin/env python
"""
This setup.py packages `upload.py` script from rietveld project
as `review.py` for PyPI, so that it could be called as::

  python -m review

To update PyPI package, issue::
   python refresh.py
   python setup.py sdist upload
"""

from distutils.core import setup

setup(
    name='review',
    version='709',
    author='Google Inc. & Co.',
    author_email='codereview-discuss@googlegroups.com',
    url='http://codereview.appspot.com/',

    description='upload script for Rietveld code review tool',
    long_description="""
Usage::

    python -m review [options]

Changes:

 On August 1st of 2011 Rietveld moved from Subversion to Mercurial.
 As a result of ommitting some branches, revision number decreased.

 `709:840f9bb917ba`_ - 2011-09-22

 - Add repository ID field to link Issue with Repository (review 5093045)
 - More fixes to fit upload.py options in one screen (review 4962070)

 `695:ba3f47e4a614`_ - 2011-09-07

 - Hide perforce options unless explicitly requested (4968071)
 - --send_patch option to attach diff instead of inline, by Kaelyn (4881041)
 - Ignore git submodules when generating diffs (issue #324, 4822044)
 - Escape @ in filenames when running SVN commands (issue #322, 4745041)
 - Remove MIMETYPES whitelist as a way to detect if file is binary (4641078)

Before moving to Mercurial:

 | r745 - Better handling of login errors, patch by proppy@goog (#289, 4547067)
 | r730 - Accept 'cvs diff' return1 either 0 or 1, by Matthew Dempsky (4435076)
 | r703 - Make RealMain() suitable for API calls (4439056)
 | r700 - -r N:M failure on new directories, by Arkadi Shishlov (#187, 4368045)
 | r687 - Fix upload.py typos, by leeight (#286, 4277081)
 | r680 - Add CVS backend, by Matthew Dempsky 4280044)
 | r654 - Preserve username in Base URL until server upload (#266, 4071042)

 | r640 - Add perforce support, by Alex McCarthy (2635043)
 | r632 - Support for Rietveld instances moved by HTTP 301 (3227041)
 | r590 - Look at the old filename only for add with Mercurial (2951041)

 | r588 - Support "http://" prefix when detecting localhost usage (2736045)
 | r585 - Fix wrong base revision for Python repository (issue #239, 2442042)

 | r579 - No depth restriction on 'hg diff' by default (issue #234, 2292041)
 | r566 - Remove "default" from help text for --verbose (2048041)
 | r561 - Locate subversion config on Windows (1983049)

 | r554 - Fix --rev option (git backend) when argument has a colon (issue #211)
 | r552 - Fix exception while trying to output an error (3109015)
 | r541 - Fix variable usage when getting/setting keyring password (1900041)
 | r538 - Fetch base file from SVN url if local history is missing (issue #208)
 | r537 - Optionally use the 'keyring' module to avoid password prompts
 | r535 - Improve captcha message for Google Apps accounts (1690047)
 | r534 - Convert Unicode values to ASCII (1590044)
 | r531 - Add account type flag to upload.py (issue #195)

.. _`709:840f9bb917ba`: http://code.google.com/p/rietveld/source/list?path=/upload.py&r=840f9bb917ba
.. _`695:ba3f47e4a614`: http://code.google.com/p/rietveld/source/list?path=/upload.py&r=ba3f47e4a614

* Home Page:   http://codereview.appspot.com/
* Development: http://code.google.com/p/rietveld/
* Discussions: http://groups.google.com/group/codereview-discuss/
* PyPI Code:   http://bitbucket.org/techtonik/python-review/
""",
    license='Apache 2.0',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
        'Topic :: Utilities',
    ],

    py_modules=['review'],
)
