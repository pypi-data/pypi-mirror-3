from setuptools import setup, find_packages
import sys, os

version = '0.2'

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
except IOError:
    README = ''

setup(name='tgext.less',
      version=version,
      description="LESS middleware for TurboGears2",
      long_description=README,
      classifiers=[
        "Environment :: Web Environment",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: TurboGears"
        ],
      keywords='turbogears2.extension LESS WSGI',
      author='Carlos Daniel Ruvalcaba Valenzuela',
      author_email='clsdaniel@gmail.com',
      url='http://bitbucket.org/clsdaniel/tgext.less',
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
