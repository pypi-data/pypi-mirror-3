from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='collective.js.ckeditor',
      version=version,
      description="Just register ckeditor resources to Plone registry",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='plone ckeditor',
      author='JeanMichel FRANCOIS',
      author_email='toutpt@gmail.com',
      url='https://github.com/toutpt/collective.js.ckeditor',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.js'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      extras_require = dict(
          test=['plone.app.testing'],
      ),
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
