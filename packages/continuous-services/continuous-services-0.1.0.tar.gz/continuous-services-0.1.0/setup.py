from distutils.core import setup
from setuptools import find_packages

from continuous_services import __version__

setup(
    name='continuous-services',
    version=__version__,
    description="Official continuous.io services integration - Access these services in your project's admin screen",
    author="Adam Charnock",
    author_email="adam@continuous.io",
    url="https://github.com/continuous/continuous-services",
    license="Dual license: Apache Software License, GPL v3",
    install_requires=[
        # Add your service's requirements here
        "dnspython",           # required by: jabber
        "xmpppy",              # required by: jabber
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 2.6",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
    ],
    packages=find_packages()
)