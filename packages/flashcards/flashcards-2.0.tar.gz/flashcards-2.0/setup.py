from setuptools import setup,find_packages
import os
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
    
setup(
    name = "flashcards",
    version = "2.0",
    author = "Jose Luis Naranjo Gomez",
    author_email = "luisnaranjo733@hotmail.com",
    description = ("A simple memory-study utility, similar to flashcards."),
    license = "GNU GPL",
    keywords = "study flashcard replacement command line utility",
    url = "http://pypi.python.org/pypi/chem",
    packages=['flashcards'],
    long_description=read('README.txt'),
    classifiers=[
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Topic :: Utilities",
    ],
)
