from distutils.core import setup
from sys import version

# Check Python version and remove "classifiers" and "download_url" if less than 2.2.3
if version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

setup(
    name='leftronic',
    version='1.3.1',
    author='Cesar Del Solar',
    author_email='support@leftronic.com',
    maintainer='Leftronic',
    maintainer_email='support@leftronic.com',
    keywords=["api", "dashboard", "leftronic"],
    py_modules=['leftronic'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    url = 'https://github.com/sonofabell/leftronic-python',
    download_url = 'https://github.com/sonofabell/leftronic-python',
    description='A Python package to interface with the Leftronic API.',
    long_description = """\

This Python package provides functions to integrate with Leftronic's information dashboards.
    * pushNumber() pushes a number to a Number, Horizontal/Vertical Bar, or Dial widget
    * pushGeo() pushes a geographic location (latitude and longitude) to a Map widget
    * pushText() pushes a title and message to a Text Feed widget
    * pushLeaderboard() pushes an array to a Leaderboard widget
    * pushList() pushes an array to a List widget

License is GNU Library or Lesser General Public License (LGPL).
A copy of the license is available at http://www.gnu.org/copyleft/lesser.html.

Public repository and documentation is on Github at https://github.com/sonofabell/leftronic-python.

"""
)

# Full list of classifiers: http://pypi.python.org/pypi?%3Aaction=list_classifiers

# Classifiers only supported in Python 2.2.3 or newer versions

# License information (GNU - LGPL): http://www.gnu.org/copyleft/lesser.html
