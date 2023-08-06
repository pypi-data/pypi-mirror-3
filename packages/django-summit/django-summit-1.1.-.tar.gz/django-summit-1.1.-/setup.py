import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages
setup(
    name = "django-summit",
    version = "1.1.-",
    packages = find_packages(),
    author = "Chris Johnston",
    author_email = "chrisjohnston@ubuntu.com",
    description = "This is the Summit Scheduling Tool",
    url = "http://launchpad.net/summit",
    include_package_data = True
)
