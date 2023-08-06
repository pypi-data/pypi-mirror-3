from setuptools import setup, find_packages
import os

# The version of the wrapped library is the starting point for the
# version number of the python package.
# In bugfix releases of the python package, add a '-' suffix and an
# incrementing integer.
# For example, a packaging bugfix release version 1.4.4 of the
# js.jquery package would be version 1.4.4-1 .

version = '1.0'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('js', 'test_root_directory_for_fanstatic_packages.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='js',
    version=version,
    description="Root directory for Fanstatic packages",
    long_description=long_description,
    classifiers=[],
    keywords='',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'setuptools',
        ],
    entry_points={
        'fanstatic.libraries': [
            'root_directory_for_fanstatic_packages = js:library',
            ],
        },
    )
