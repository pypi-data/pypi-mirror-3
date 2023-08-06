from setuptools import setup, find_packages
import os

# The version of the wrapped library is the starting point for the
# version number of the python package.
# In bugfix releases of the python package, add a '-' suffix and an
# incrementing integer.
# For example, a packaging bugfix release version 1.4.4 of the
# js.jquery package would be version 1.4.4-1 .

version = '0.10.0'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('js', 'crossroads', 'test_crossroads.js.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='js.crossroads',
    version=version,
    description="Fanstatic packaging of Crossroads.js",
    long_description=long_description,
    classifiers=[],
    keywords='',
    license='MIT',
    packages=find_packages(),namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'js.signals',
        'setuptools',
        ],
    entry_points={
        'fanstatic.libraries': [
            'crossroads.js = js.crossroads:library',
            ],
        },
    )
