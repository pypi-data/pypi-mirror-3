import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'pyramid_debugtoolbar',
    'waitress',
    'ewsclient',
    'python-dateutil<2.0'
    ]

setup(name='ewscal',
      version='0.0',
      description='Render Exchange calendars to SVG using d3.js',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Daniel Holth',
      author_email='dholth@fastmail.fm',
      url='',
      license='MIT',
      keywords='web pyramid pylons',
      packages=['ewscal'],
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="ewscal",
      entry_points = """\
      [paste.app_factory]
      main = ewscal:main
      """,
      )

