from setuptools import setup

import sys
import os

setup(
    name="inquire",
    version=__import__("inquire").__version__,
    description="Simplified collection and object querying for Python.",
    author="Tony Young",
    author_email="rofflwaffls@gmail.com",
    packages=[ "inquire" ]
)