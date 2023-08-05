# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

from setuptools import setup, find_packages


setup(
    name='gocept.exttest',
    version='0.1.4',
    author='gocept',
    author_email='mail@gocept.com',
    url='http://code.gocept.com/hg/public/gocept.exttest',
    description="Helper to integrate external tests with python unittests.",
    long_description=(
        open('README.txt').read()
        + '\n\n'
        + open('CHANGES.txt').read()),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='ZPL',
    namespace_packages=['gocept'],
    install_requires=[
        'setuptools',
        'zc.recipe.testrunner',
    ],
    extras_require=dict(test=[
        'mock',
    ]),
)
