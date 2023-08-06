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
    'grokcore.view[test]',
    'zope.app.wsgi',
    'zope.configuration',
    'zope.securitypolicy',
    'zope.testing',
    ]

setup(
    name='grokcore.security',
    version='1.6',
    author='Grok Team',
    author_email='grok-dev@zope.org',
    url='http://grok.zope.org',
    download_url='http://pypi.python.org/pypi/grokcore.security',
    description='Grok-like configuration for Zope security components',
    long_description=long_description,
    license='ZPL',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Framework :: Zope3',
        ],
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages=['grokcore'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'grokcore.component >= 2.1',
        'martian >= 0.13',
        'zope.component',
        'zope.interface',
        'zope.security',
        ],
    tests_require=tests_require,
    extras_require={
        'role': [
            'zope.securitypolicy',
            ],
        'test': tests_require
        },
)
