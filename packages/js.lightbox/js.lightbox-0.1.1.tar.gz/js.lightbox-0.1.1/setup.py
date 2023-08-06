from setuptools import setup, find_packages
import os

version = '0.1.1'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('js', 'lightbox', 'test_lightbox.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='js.lightbox',
    version=version,
    description="fanstatic jquery lightbox.",
    long_description=long_description,
    classifiers=[],
    keywords='fanstatic jquery lightbox',
    author='Andrew Mleczko',
    url = 'https://github.com/amleczko/js.lightbox',
    author_email='andrew@mleczko.net',
    license='GPL',
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
            'lightbox = js.lightbox:library',
            ],
        },
    )
