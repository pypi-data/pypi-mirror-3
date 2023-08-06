#!/usr/bin/env python
import os
from setuptools import setup, find_packages
from djangopipstarter import get_version

setup(name='django-pip-starter',
      version=get_version(),
      author='Marius Grigaitis',
      author_email='m@mar.lt',
      description='Useful tool for quickstarting django projects.'
                  'It creates virtual environment and preconfigured django project',
      license='BSD',
      keywords='django pip starter bootstrap initial create',
      url='https://bitbucket.org/marltu/django-pip-starter',
      packages=find_packages(),
      package_data={'djangopipstarter': ['template/Makefile', 'template/config/*.txt', 'template/config/*.sample', 'template/project/*.sample', 'template/project/*.json', 'template/project/*.py', 'template/project/templates/*.html', 'template/project/static/css/*.css']},
      scripts=['djangopipstarter/bin/django-pip-starter.py'],
      long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
      classifiers=['Development Status :: 4 - Beta',
                  'Framework :: Django',
                  'Intended Audience :: Developers',
                  'Intended Audience :: System Administrators',
                  'License :: OSI Approved :: BSD License',
                  'Operating System :: POSIX :: Linux',
                  'Programming Language :: Python',
                  'Programming Language :: Python :: 2',
                  'Programming Language :: Python :: 2.4',
                  'Programming Language :: Python :: 2.5',
                  'Programming Language :: Python :: 2.6',
                  'Programming Language :: Python :: 2.7',
                  'Programming Language :: Python :: 2 :: Only',
                  'Topic :: Software Development',
                  'Topic :: Software Development :: Build Tools',
                  'Topic :: Software Development :: Code Generators',
                  'Topic :: Software Development :: Libraries :: Application Frameworks'])
