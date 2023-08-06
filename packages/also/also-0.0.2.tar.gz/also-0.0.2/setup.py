import os
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="also",
    version="0.0.2",
    packages=["also"],
    author="Huan Do",
    author_email="doboy0@gmail.com",
    long_description=read('README.md'),
    url="https://github.com/Doboy/Also",
    )
