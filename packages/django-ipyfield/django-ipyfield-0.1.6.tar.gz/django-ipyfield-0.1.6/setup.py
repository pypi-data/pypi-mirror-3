from setuptools import setup, find_packages
import sys, os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import ipyfield

setup(
    name="django-ipyfield",
    version=ipyfield.__version__,
    url="https://bitbucket.org/onelson/django-ipyfield/",
    author="Owen Nelson",
    author_email="onelson@gmail.com",
    license="MIT",
    description="IPy.IP instances with BigInt storage for django models",
    long_description=open('README.rst').read(),
    keywords="ip, models, django",
    packages=["ipyfield"],
    setup_requires=["setuptools"],
    install_requires=("setuptools", "IPy", "django",),
    classifiers=(
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",),
)

