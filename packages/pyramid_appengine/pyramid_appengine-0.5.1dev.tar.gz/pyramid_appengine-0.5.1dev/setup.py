from setuptools import setup, find_packages
import os
here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'readme.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

version = "0.5.1"
requires = ["pastescript"]
setup(name='pyramid_appengine',
      version=version,
      description="Scaffold + Tools for creating/developing pyramid applications on Google App Engine",
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
          ],
      keywords='web pyramid pylons google-app-engine',
      author='Tom Willis',
      author_email='tom@batterii.com',
      url='https://github.com/twillis/pyramid_appengine',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      entry_points="""
      # -*- Entry points: -*-
      [paste.paster_create_template]
      appengine_starter=pyramid_appengine.scaffolds:PyramidAppEngineStarterTemplate
      """,
      )
