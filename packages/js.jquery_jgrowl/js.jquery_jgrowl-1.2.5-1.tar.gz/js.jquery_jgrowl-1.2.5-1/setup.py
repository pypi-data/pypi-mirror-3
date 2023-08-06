from setuptools import setup, find_packages
import os

version = '1.2.5-1'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('js', 'jquery_jgrowl', 'test_jquery_jgrowl.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='js.jquery_jgrowl',
    version=version,
    description="fanstatic jQuery jGrowl.",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Fanstatic Developers',
    author_email='fanstatic@googlegroups.com',
    license='BSD',
    packages=find_packages(),
    namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'js.jquery',
        'setuptools',
        ],
    entry_points={
        'fanstatic.libraries': [
            'jquery_jgrowl = js.jquery_jgrowl:library',
            ],
        },
    )
