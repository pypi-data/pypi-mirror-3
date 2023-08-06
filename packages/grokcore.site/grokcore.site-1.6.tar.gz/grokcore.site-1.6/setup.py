from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    )

tests_require = [
    'zope.app.appsetup',
    'zope.component',
    'zope.configuration',
    'zope.location',
    'zope.testing',
    'grokcore.content',
    ]

setup(
    name='grokcore.site',
    version='1.6',
    author='Grok Team',
    author_email='grok-dev@zope.org',
    url='http://grok.zope.org',
    download_url='http://pypi.python.org/pypi/grokcore.site',
    description='Grok-like configuration for Zope local site and utilities',
    long_description=long_description,
    license='ZPL',
    classifiers=['Environment :: Web Environment',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: Zope Public License',
                 'Programming Language :: Python',
                 'Framework :: Zope3',
                 ],

    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['grokcore'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['setuptools',
                      'ZODB3',
                      'zope.event',
                      'grokcore.component >= 2.1',
                      'martian >= 0.13',
                      'zope.annotation',
                      'zope.component',
                      'zope.container',
                      'zope.interface',
                      'zope.lifecycleevent',
                      'zope.site',
                      ],
    tests_require=tests_require,
    extras_require={'test': tests_require},
)
