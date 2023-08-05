# Elatom's setup.py
# classifiers from http://pypi.python.org/pypi?%3Aaction=list_classifiers
from distutils.core import setup

setup(
    name="Elatom",
#    packages=["elatom"],
    version="1.0",
    description="Podcast downloader in Python 3",
    author="Eliovir",
    author_email="eliovir@gmail.com",
    url="https://launchpad.net/elatom",
    #download_url=
    keywords=["podcast", "rss", "atom"],
    classifiers = [
        "Topic :: Internet",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Console :: Curses",
        "Intended Audience :: End Users/Desktop",
        "Environment :: Other Environment",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Natural Language :: Esperanto",
        "Natural Language :: French"
    ],
    long_description = """\
A podcast downloader developed in Python 3 with Curses and Tkinter interfaces.

It can also be used in crontab to grab automatically the new media.
It reads RSS 2.0 and Atom 1.0. All files are downloaded simultaneously to speed up total download.
It aims to be a single file for basic features, to facilitate the install.
Additional files provide translations (Esperanto, French), or unit tests.
""",
    data_files=[('share/applications', ['elatom.desktop']), ('share/pixmaps', ['elatom.png'])]
)
