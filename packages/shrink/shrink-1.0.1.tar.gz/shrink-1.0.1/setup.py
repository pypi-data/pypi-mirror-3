import os

from setuptools import find_packages
from setuptools import setup

from shrink import __version__
from shrink import read_file


CURRENT_DIR = os.path.dirname(__file__)
README = read_file(CURRENT_DIR, "README.rst")
CHANGELOG = read_file(CURRENT_DIR, "CHANGELOG.rst")
LONG_DESCRIPTION = u"{0}\n\n{1}".format(README, CHANGELOG)
AUTHORS = (
    ("Jer\xc3\xb3nimo Jos\xc3\xa9 Albi", "albi@wienfluss.net"),
)


setup(
    name="shrink",
    version=__version__,
    author=", ".join([a[0] for a in AUTHORS]),
    author_email=", ".join([a[1] for a in AUTHORS]),
    description="Tool for minification of css and javascript files",
    long_description=LONG_DESCRIPTION,
    url="https://bitbucket.org/jeronimoalbi/shrink",
    keywords="minify javascript css yuicompressor",
    license="BSD License",
    platforms=["OS Independent"],
    zip_safe=False,
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Utilities",
    ],
    entry_points={
        'console_scripts': [
            "shrink = shrink.command:run",
        ],
    },
)
