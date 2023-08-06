from setuptools import setup, find_packages
import sys, os

version = '0.0.1'

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
except IOError:
    README = ''

setup(name='tgext.minify',
      version=version,
      description="CSS and JS minifier for TurboGears2",
      long_description=README,
      classifiers=[
        "Environment :: Web Environment",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: TurboGears"
        ],
      keywords='turbogears2.extension CSS JS minify WSGI',
      author='Simone Marzola',
      author_email='simone.marzola@axant.it',
      url='http://bitbucket.org/simock85/tgext.minify',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages=['tgext'],
      include_package_data=True,
      package_data = {'':['*.html', '*.js', '*.css', '*.png', '*.gif']},
      zip_safe=False,
      install_requires=[
        "TurboGears2 >= 2.0b7",
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
