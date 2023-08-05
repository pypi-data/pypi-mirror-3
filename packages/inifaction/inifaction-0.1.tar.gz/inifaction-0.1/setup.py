from setuptools import setup, find_packages
import sys, os

version = '0.1'
description = 'Manage your Webfaction settings in a per project basis from an INI style file.'
long_description = open('README.rst').read()

setup(name='inifaction',
      version=version,
      description=description,
      long_description=long_description,
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.6',
          'Topic :: Utilities',
          ],
      keywords='webfaction, api, xml, rpc, ini, configuration',
      author='Unai Zalakain (GISA)',
      author_email='unai@gisa-elkartea.org',
      url='https://lagunak.gisa-elkartea.org/projects/inifaction/',
      license='LICENSE.txt',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      package_data = {'': ['*.ini']},
      zip_safe=False,
      install_requires=['xmlrpclib', 'configobj'],
      entry_points={'console_scripts': ['inifaction = inifaction.main:main']},
      )
