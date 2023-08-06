from setuptools import setup, find_packages
import os

# The version of the wrapped library is the starting point for the
# version number of the python package.
# In bugfix releases of the python package, add a '-' suffix and an
# incrementing integer.
# For example, a packaging bugfix release version 1.4.4 of the
# js.jquery package would be version 1.4.4-1 .

version = '0.2.0'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('js', 'angular_ui', 'test_angularui.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='js.angular_ui',
    version=version,
    description="Fanstatic packaging of AngularUI",
    long_description=long_description,
    classifiers=[],
    keywords='',
    license='MIT',
    packages=find_packages(),namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'js.angular',
        'setuptools',
        ],
    entry_points={
        'fanstatic.libraries': [
            'angularui = js.angular_ui:library',
            ],
        },
    )
