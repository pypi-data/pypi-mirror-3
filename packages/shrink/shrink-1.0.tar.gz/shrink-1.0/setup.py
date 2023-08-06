import os

from setuptools import find_packages
from setuptools import setup

from shrink import __version__


README_FILE = os.path.join(os.path.dirname(__file__), "README.rst")
AUTHORS = (
    ("Jer\xc3\xb3nimo Jos\xc3\xa9 Albi", "albi@wienfluss.net"),
)


setup(
    name="shrink",
    version=__version__,
    author=", ".join([a[0] for a in AUTHORS]),
    author_email=", ".join([a[1] for a in AUTHORS]),
    description="Tool for minification of css stylesheets and javascript files",
    url="https://bitbucket.org/jeronimoalbi/shrink",
    keywords="minify javascript css yuicompressor",
    license="BSD License",
    platforms=["OS Independent"],
    zip_safe=True,
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
