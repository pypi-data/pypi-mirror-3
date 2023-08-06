import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages
setup(
    name = "pylemon-test",
    version = "0.1",
    packages = find_packages(),
    author = "pyLemon",
    author_email = "leeway1985@gmail.com",
    description = "A package to test how to use pypi",
    url = "https://github.com/pylemon/",
    include_package_data = True
)
