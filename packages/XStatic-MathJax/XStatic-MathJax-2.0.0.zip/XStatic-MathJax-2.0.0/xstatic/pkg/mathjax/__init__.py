"""
XStatic resource package

See package 'XStatic' for documentation and basic tools.
"""

DISPLAY_NAME = 'MathJax' # official name, upper/lowercase allowed
PACKAGE_NAME = 'XStatic-%s' % DISPLAY_NAME # name used for PyPi

NAME = __name__.split('.')[-1] # package name (e.g. 'foo' or 'foo_bar')
                               # please use a all-lowercase valid python
                               # package name

VERSION = '2.0' # for simplicity, use same version x.y.z as bundled files
                 # additionally we append .b for our build number, so we
                 # can release new builds with fixes for xstatic stuff.
BUILD = '0' # our package build number, so we can release new builds
            # with fixes for xstatic stuff.

PACKAGE_VERSION = VERSION + '.' + BUILD # version used for PyPi

DESCRIPTION = "%s %s (XStatic packaging standard)" % (DISPLAY_NAME, VERSION)

PLATFORMS = 'any'
CLASSIFIERS = []
KEYWORDS = '%s xstatic' % NAME

# XStatic-* package maintainer:
MAINTAINER = 'Reimar Bauer'
MAINTAINER_EMAIL = 'rb.proj@googlemail.com'

# this refers to the project homepage of the stuff we packaged:
HOMEPAGE = 'http://www.mathjax.org'

# this refers to all files:
LICENSE = '(same as %s)' % DISPLAY_NAME

from os.path import join, dirname
BASE_DIR = join(dirname(__file__), 'data')
# linux package maintainers just can point to their file locations like this:
#BASE_DIR = '/usr/share/javascript/mathjax

LOCATIONS = {
        # if value is a string, it is a base location, just append relative
        # path/filename. if value is a dict, do another lookup using the
        # relative path/filename you want.
        # your relative path/filenames should usually be without version
        # information, because either the base dir/url is exactly for this
        # version or the mapping will care for accessing this version.
        ('mathjax', 'http'): 'http://cdn.mathjax.org/mathjax/%s-latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML' % VERSION,
        ('mathjax', 'https'): 'https://d3eoax9i5htok0.cloudfront.net/mathjax/%s-latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML' % VERSION,
    }



"""
MathJax package
"""

from os.path import join, dirname

try:
    from xstatic.main import XStatic
except ImportError:
    class XStatic(object):
        """
        just a dummy for the time when setup.py is running and
        for the case that xstatic is not already installed.
        """

class MathJax(XStatic):
    name = 'mathjax' # short, all lowercase name
    display_name = 'MathJax' # official name, upper/lowercase allowed
    version = '2.0.0'     # for simplicity, use same version x.y.z as bundled files
                          # additionally we append .b for our build number, so we
                          # can release new builds with fixes for xstatic stuff.

    base_dir = join(dirname(__file__), 'data')
    # linux package maintainers just can point to their file locations like this:
    # base_dir = '/usr/share/java/twikidraw-moin'

    description = "%s (XStatic packaging standard)" % display_name

    platforms = 'any'
    classifiers = []
    keywords = '%s xstatic' % name

    # this all refers to the XStatic-* package:
    author = 'Reimar Bauer'
    author_email = 'rb.proj@googlemail.com'
    # XXX shall we have another bunch of entries for the bundled files?
    # like upstream_author/homepage/download/...?
    # note: distutils/register can't handle author and maintainer at once.

    # this refers to the project homepage of the stuff we packaged:
    homepage = 'http://www.mathjax.org'

    # this refers to all files:
    license = '(same as %s)' % display_name

    locations = {
        # if value is a string, it is a base location, just append relative
        # path/filename. if value is a dict, do another lookup using the
        # relative path/filename you want.
        # your relative path/filenames should usually be without version
        # information, because either the base dir/url is exactly for this
        # version or the mapping will care for accessing this version.
        ('mathjax', 'http'): 'http://cdn.mathjax.org/mathjax/1.1-latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML',
        ('mathjax', 'https'): 'https://d3eoax9i5htok0.cloudfront.net/mathjax/1.1-latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML',
    }


