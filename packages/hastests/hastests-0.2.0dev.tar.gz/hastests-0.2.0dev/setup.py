from setuptools import setup, find_packages
import sys, os

execfile('hastests/version.py')

setup(name='hastests',
      version=__version__,
      description="HasTests API for Python",
      long_description="See `HasTests API for Python <https://github.com/spawngrid/hastests-python>`_ for more information.",
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Topic :: Software Development :: Testing',
          'Topic :: Software Development :: Quality Assurance',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3'
      ],
      keywords='test tests testing hastests conceptscript json generation data TDD spawngrid',
      author='Spawngrid, Inc.',
      author_email='team@spawngrid.com',
      url='http://github.com/spawngrid/hastests-python',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
