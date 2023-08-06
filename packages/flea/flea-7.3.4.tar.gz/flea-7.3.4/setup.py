from setuptools import setup, find_packages
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
    name='flea',
    version=read('VERSION.txt').strip().encode('ASCII'),
    description="Test WSGI applications",
    long_description=read('README.txt') + '\n\n' + read('CHANGELOG.txt'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Testing',
    ],
    keywords='',
    author='Oliver Cope',
    author_email='oliver@redgecko.org',
    url='http://ollycope.com/software/flea/',
    license='BSD',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'pesto>=16',
        'lxml',
        'cssselect',
        # -*- Extra requirements: -*-
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,
)
