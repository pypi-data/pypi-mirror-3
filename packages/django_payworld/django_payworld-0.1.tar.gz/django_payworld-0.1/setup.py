import os
from setuptools import setup

# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "django_payworld",
    version = "0.1",
    author = "Ivan A. Anishchuk",
    author_email = "anishchuk_ia@lavabit.com",
    description = ("Intergration pay-world.ru for django projects"),
    license = "CC0",
    keywords = "payment django integration",
    url = "https://bitbucket.com/ib_soft/django_payworld",
    packages=['django_payworld'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Programming Language :: Python :: 2 :: Only",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
    ],
    install_requires=[
        'setuptools',
        'django',
    ],
)
