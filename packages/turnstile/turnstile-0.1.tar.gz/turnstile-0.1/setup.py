import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='turnstile',
    version='0.1',
    author='Kevin L. Mitchell',
    author_email='kevin.mitchell@rackspace.com',
    description="Distributed rate-limiting middleware",
    license='Apache License (2.0)',
    packages=['turnstile'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Paste',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
        ],
    url='https://github.com/klmitch/turnstile',
    long_description=read('README.rst'),
    entry_points={
        'paste.filter_factory': [
            'turnstile = turnstile.middleware:turnstile_filter',
            ],
        'console_scripts': [
            'setup_limits = turnstile.tools:setup_limits',
            'dump_limits = turnstile.tools:dump_limits',
            ],
        },
    install_requires=[
        'argparse',
        'eventlet',
        'lxml',
        'metatools',
        'msgpack-python',
        'redis',
        'routes',
        ],
    tests_require=[
        'stubout',
        ],
    )
