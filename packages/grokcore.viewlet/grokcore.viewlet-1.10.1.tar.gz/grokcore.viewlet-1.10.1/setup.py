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
    'zope.annotation',
    'zope.app.appsetup',
    'zope.app.publication',
    'zope.app.wsgi',
    'zope.configuration',
    'zope.container',
    'zope.principalregistry',
    'zope.securitypolicy',
    'zope.site',
    'zope.testing',
    'zope.traversing',
    ]

setup(
    name='grokcore.viewlet',
    version='1.10.1',
    author='Grok Team',
    author_email='grok-dev@zope.org',
    url='http://grok.zope.org',
    download_url='http://cheeseshop.python.org/pypi/grokcore.viewlet',
    description='Grok-like configuration for zope viewlets',
    long_description=long_description,
    license='ZPL',
    classifiers=['Environment :: Web Environment',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: Zope Public License',
                 'Programming Language :: Python',
                 'Framework :: Zope3',
                 ],
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages=['grokcore'],
    include_package_data = True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'grokcore.component >= 2.5',
        'grokcore.security >= 1.6',
        'grokcore.view >= 2.7',
        'martian >= 0.14',
        'zope.viewlet',
        'zope.contentprovider',
        'zope.browserpage',
        'zope.component',
        'zope.interface',
        'zope.publisher',
        'zope.security',
        ],
    tests_require=tests_require,
    extras_require={'test': tests_require},
)
