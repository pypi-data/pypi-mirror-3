from setuptools import setup
import os


README_FILE = open('README.md')
try:
    LONG_DESCRIPTION = README_FILE.read()
finally:
    README_FILE.close()

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, 'djangoproject_wizard', 'project_template')
STARTPROJECT_DATA = []
for path, dirs, filenames in os.walk(DATA_DIR):
    # Ignore directories that start with '.'
    for i, dir in enumerate(dirs):
        if dir.startswith('.'):
            del dirs[i]
    path = path[len(DATA_DIR) + 1:]
    STARTPROJECT_DATA.append(os.path.join('project_template', path, '*.*'))
    # Get files starting with '.' too (they are excluded from the *.* glob).
    STARTPROJECT_DATA.append(os.path.join('project_template', path, '.*'))


setup(name='djangoproject_wizard',
      version='1.0a',
      author='Modified by Gilson Filho (Source: Lincoln Loop)',
      author_email='contato@gilsondev.com',
      description=('Create a Django project layout based on Lincoln Loop '
                     'best practices.'),
      long_description=LONG_DESCRIPTION,
      packages=['djangoproject_wizard'],
      package_data={'djangoproject_wizard': STARTPROJECT_DATA},
      scripts=['bin/djangoproject-wizard.py'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Web Environment',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules'])
