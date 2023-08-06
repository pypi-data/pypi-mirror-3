import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'ipaddr',
    'pyramid',
    'pyramid_debugtoolbar',
    'pyramid_jinja2',
    'pyramid_tm',
    'retools',
    'SQLAlchemy',
    'transaction',
    'waitress',
    'zope.sqlalchemy',
    ]

setup(name='sharder',
      version='0.0',
      description='Screenshot web page fragments and serve through wsgi.',
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
      packages=['sharder'],
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      entry_points = """\
      [paste.app_factory]
      main = sharder:main
      """,
      )

