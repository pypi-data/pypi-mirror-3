from setuptools import setup, find_packages
from htmlmin import __version__

README = open('README.rst').read()

setup(name='django-htmlmin',
      version=__version__,
      description='html minify for django',
      long_description=README,
      author='CobraTeam',
      author_email='andrewsmedina@gmail.com',
      packages=find_packages(),
      include_package_data=True,
      test_suite='nose.collector',
      install_requires=['argparse', 'django', 'BeautifulSoup'],
      tests_require=['nose', 'coverage'],
      entry_points = {
          'console_scripts' : [
              'pyminify = htmlmin.commands:main',
          ]
      },
     )
