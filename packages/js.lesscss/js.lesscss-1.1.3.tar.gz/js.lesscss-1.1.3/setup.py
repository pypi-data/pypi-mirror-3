from setuptools import setup, find_packages
import os

version = '1.1.3'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('js', 'lesscss', 'test_less.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='js.lesscss',
    version=version,
    description="Fanstatic packaging of less",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Stephane Klein',
    author_email='stephane@harobed.org',
    license='BSD',
    packages=find_packages(), namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'setuptools',
        ],
    entry_points={
        'fanstatic.libraries': [
            'less = js.lesscss:library',
            ],
        'console_scripts': [
            'jslessc = js.lesscss:main',
            ],
        },
    )
