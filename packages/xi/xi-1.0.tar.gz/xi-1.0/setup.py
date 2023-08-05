from distutils.core import setup


setup(
    name = "xi",
    version = "1.0",
    author = "startling",
    author_email = "tdixon51793@gmail.com",
    description = "A little script for copying and pasting through unix pipes.",
    scripts = ['scripts/xi'],
    install_requires = ['clint', 'xerox'],
    keywords = ['paste', 'copy', 'copypaste', 'pipes'],
    classifiers = [
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Environment :: Console"
    ]
)
