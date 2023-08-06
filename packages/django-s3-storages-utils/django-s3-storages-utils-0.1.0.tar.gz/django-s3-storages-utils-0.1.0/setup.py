from setuptools import setup, find_packages

VERSION = '0.1.0'

LONG_DESCRIPTION = open('README.rst').read()

setup(name='django-s3-storages-utils',
    version=VERSION,
    description="django-s3-storages-utils - Utilities for setting up s3 for use with django-storages",
    long_description=LONG_DESCRIPTION,
    author='Reuven V. Gonzales',
    author_email='reuven@tobetter.us',
    url="https://github.com/ravenac95/django-s3-storages-utils",
    license='MIT',
    platforms='Unix',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'django-storages',
        'boto',
    ],
    entry_points={},
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: POSIX',
    ],
)
