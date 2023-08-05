# The README.txt file should be written in reST so that PyPI can use
# it to generate your project's PyPI page. 
long_description = open('README.txt').read()

from setuptools import setup, find_packages

setup(
    name="wiki2sphinx",
    version=0.2,
    description="tool for creating a sphinx document structure from a ReST-moin-wiki",
    long_description=long_description,
    classifiers="Development Status :: 5 - Production/Stable",
    keywords="python, MoinMoin",
    author="Henning Fleddermann",
    author_email="zhick666@googlemail.com",
    maintainer="Henning Fleddermann",
    maintainer_email="zhick666@googlemail.com",
    license="GPL",
    url="https://utils.icg.kfa-juelich.de/hg/wiki2sphinx/0.2/",
    platforms="any",
    packages=find_packages(),
    namespace_packages=[],
    include_package_data=True,
    zip_safe=False,
    install_requires=["argparse", ],
    entry_points = dict(
        console_scripts = [
                           'Wiki2Sphinx = wiki2sphinx.Wiki2Sphinx:main'],
    ),
)
