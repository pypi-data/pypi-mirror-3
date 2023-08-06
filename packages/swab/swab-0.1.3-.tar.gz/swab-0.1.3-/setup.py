from setuptools import setup, find_packages
import sys
import os
def read(*path):
    """
    Read and return content from ``path``
    """
    f = open(
        os.path.join(
            os.path.dirname(__file__),
            *path
        ),
        'r'
    )
    try:
        return f.read().decode('UTF-8')
    finally:
        f.close()


setup(
    name='swab',
    version=read('VERSION.txt').encode('ASCII'),
    description="Swab: Simple WSGI A/B testing",
    long_description=read('README.txt') + '\n\n' + read('CHANGELOG.txt'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
    ],
    keywords='',
    author='Oliver Cope',
    author_email='oliver@redgecko.org',
    url='',
    license='BSD',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    package_data = {'': ['static/*', 'templates/*',]},
    zip_safe=False,
    install_requires=[
        u'pesto>=22dev',
        u'pestotools.genshi',
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
    entry_points="""
    """,
    dependency_links=[]
)
