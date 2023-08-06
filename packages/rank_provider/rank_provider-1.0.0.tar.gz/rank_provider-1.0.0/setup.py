from distutils.core import setup

setup(
    name = "rank_provider",
    py_modules = ["rank_provider"],
    version = "1.0.0",
    description = "determine page rankings from Google and Alexa",
    author = "Adam Black",
    author_email = "ablack@fastmail.net",
    url = "http://github.com/aablack/",
    keywords = ["rank", "pagerank", "google", "alexa"],
    classifiers = [
        "Programming Language :: Python :: 2",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        ],
    long_description = """\
Obtain the rank/popularity of a URI from a rank provider. Currently
the supported providers are Google and Alexa.
"""
)
