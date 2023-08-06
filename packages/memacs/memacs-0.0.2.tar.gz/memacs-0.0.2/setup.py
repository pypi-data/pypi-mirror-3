from distutils.core import setup

setup(
    name = "memacs",
    packages = ["bin","memacs","memacs/lib", "memacs/lib/tests", "memacs/tests"],
    version = "0.0.2",
    description = "parse sources to org-mode files",
    author = "Armin Wieser",
    author_email = "armin.wieser@gmail.com",
    url = "https://github.com/novoid/Memacs",
    download_url = "https://github.com/novoid/Memacs/zipball/master",
    keywords = ["org-mode", "org"],
    scripts = ["bin/memacs-*.py"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",

        ],
    long_description = """\
Memacs
-----------------------------
*What were you doing* on February 14th of 2007? On *which tasks* were
you working on that very day you met your girl friend? When was the
*last appointments* with your dentist? *Who called* you on telephone
during that meeting with your customer last month?

Most people can not answer such questions. *With Memacs you can!*

Memacs extracts metadata (subjects, timestamps, contact information,
...) from many different existing data sources (file names, emails,
tweets, bookmarks, ...) on your computer and generates files which are
readable by GNU Emacs with Org-mode.    
"""
)