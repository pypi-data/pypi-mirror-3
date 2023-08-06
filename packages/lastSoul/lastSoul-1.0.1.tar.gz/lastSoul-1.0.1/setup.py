# -*- coding: iso-8859-15 -*-
from distutils.core import setup
from lastsoul._version import __version__

setup(
    name = "lastSoul",
    requires = ["PyQT",],
    version = __version__,
    packages = ["lastsoul"],
    license = "GNU General Public License v3 (GPLv3)",
    description = "Python (not yet)full scale client for IONIS's students (EPITECH/EPITA/etc)",
    author = "Mickaël FALCK",
    author_email = "lastmikoi+py@gmail.com",
    url = "https://bitbucket.org/lastmikoi/lastsoul",
    keywords = ["netsoul", "ncurses", "pyqt", "epitech", "ionis"],
    classifiers = [
      "Programming Language :: Python :: 3",
      "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
      "Operating System :: OS Independent",
      "Development Status :: 4 - Beta",
      "Environment :: X11 Applications :: Qt",
      "Environment :: Console :: Curses",
      "Environment :: Console",
      "Intended Audience :: End Users/Desktop",
      "Topic :: Communications :: Chat",
      ],
    long_description = """\
Python (not yet)full scale client for IONIS's students (EPITECH/EPITA/etc)
----------------------------------------

Features :
- Connection to netsoul server and authentification using config file
- Configuration generator script
- Multithreaded queuing system for processing in and out operations without blocking calls.
- Advanced handling with registration system of function called when regexp match with input
- Severals UI:
  * Raw command mode : allow to type commands directly to the server while being authed
  * PyQt Interface : with multi-tab, and userlist support
  * ncurses Interface : with user tracking
"""
)
