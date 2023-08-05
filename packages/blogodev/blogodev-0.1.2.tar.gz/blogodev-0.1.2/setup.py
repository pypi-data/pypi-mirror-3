from setuptools import setup, find_packages
import sys
import os
import re

extra = {}
if sys.version_info >= (3, 0):
    extra.update(
        use_2to3=True,
    )


readme = os.path.join(os.path.dirname(__file__), 'README.rst')

setup(name='blogodev',
      version="0.1.2",
      description="An interim front end for blogofile development",
      long_description=open(readme).read(),
      url="https://bitbucket.org/zzzeek/blogodev",
      classifiers=[
      'Development Status :: 3 - Alpha',
      'Environment :: Console',
      'Intended Audience :: Developers',
      'Programming Language :: Python',
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: Implementation :: CPython',
      'Programming Language :: Python :: Implementation :: PyPy',
      ],
      keywords='Blogofile',
      author='Mike Bayer',
      author_email='mike@zzzcomputing.com',
      license='MIT',
      packages=['blogodev'],
      tests_require = ['nose >= 0.11'],
      test_suite = "nose.collector",
      zip_safe=False,
      install_requires=[
            'Blogofile==0.7.1'
      ],
      entry_points = {
        'console_scripts': [ 'blogodev = blogodev:main' ],
      },
      **extra
)
