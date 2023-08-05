#!/usr/bin/env python

from distutils.core import setup

setup(name='taskl',
      version='0.1',
      description='Distributed task tracker',
      author='Denis Chernienko; Ilya Petrov',
      author_email='denekurich@gmail.com; ilya.muromec@gmail.com',
      url='https://github.com/DenekUrich/taskl',
      packages=['taskl', ],
      license = "BSD",
      entry_points={
          'console_scripts': ['tl = taskl:main'],
      },
      install_requires=[
        'requests',
        'consoleargs',
        'PyYaml',
      ],
)
