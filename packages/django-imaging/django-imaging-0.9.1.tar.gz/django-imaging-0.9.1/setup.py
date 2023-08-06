import os
from setuptools import setup

def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except: # pip doesn't support readmes apparently?
        pass

setup(
        name = "django-imaging",
        version = "0.9.1",
        author = "Jakub Nawalaniec",
        author_email = "pielgrzym@prymityw.pl",
        description = ("AJAX driven gallery field for django"),
        license = "GNU GPL v2",
        keywords = "django",
        url = "https://github.com/pielgrzym/django-imaging",
        packages = ['django-imaging'],
        long_description = read("OLD_README.txt"),
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Framework :: Django",
            "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
            ],
        )
