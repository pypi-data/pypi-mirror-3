# Copyright (c) 2012 Sebastian Wehrmann
# See also LICENSE.txt

import os.path
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(
    name='sw.grokcore.jsonp',
    version='0.1',
    url='https://bitbucket.org/sweh/sw.grokcore.jsonp',
    license='ZPL 2.1',
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent'],
    description='JSON-P base view for Grok.',
    long_description = (read('README.txt')
                         + '\n\n' +
                         read('CHANGES.txt')
    ),
    keywords=['grok', 'json-p', 'jsonp', 'jquery'],
    author='Sebastian Wehrmann',
    author_email='sebastian.wehrmann@me.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['sw', 'sw.grokcore'],
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'grokcore.json',
    ],
    extras_require={
        'test': [
            'grokcore.json [test]',
        ],
    },
)
