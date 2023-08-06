import codecs
from os.path import join, dirname
from setuptools import setup


version = '1.0'
read = lambda *rnames: unicode(codecs.open(join(dirname(__file__), *rnames),
                                           encoding='utf-8').read()
                              ).strip()

setup(
    name='django-bosssearch',
    version=version,
    description='Search with Yahoo BOSS!',
    long_description='\n\n'.join((read('README'), read('CHANGES'),)),
    author='Jaap Roes (Eight Media)',
    author_email='jaap@eight.nl',
    url='https://bitbucket.org/jaap3/django-bosssearch/',
    package_dir={'': 'src'},
    packages=['djangobosssearch', 'djangobosssearch.providers'],
    include_package_data=True,
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    install_requires=[
        'oauth',
        'django-pagination',
    ],
    tests_require=['Django>=1.2', 'unittest2>=0.5.1'],
    test_suite='tests.runtests.runtests',
    zip_safe=False,
)
