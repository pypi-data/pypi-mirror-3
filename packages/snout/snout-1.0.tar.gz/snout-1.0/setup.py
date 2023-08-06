from distutils.core import setup
PACKAGE = "snout"
NAME = "snout"
DESCRIPTION = "django url pattern generation via inspection"
AUTHOR = "mark neyer"
AUTHOR_EMAIL = "mneyer@gmail.com"
URL = "https://github.com/neyer/snout"
VERSION = __import__(PACKAGE).__version__
with open("README.md") as readme_file:
    readme_text = readme_file.read()

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=readme_text,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="BSD",
    url=URL,
    packages=[PACKAGE]
)
