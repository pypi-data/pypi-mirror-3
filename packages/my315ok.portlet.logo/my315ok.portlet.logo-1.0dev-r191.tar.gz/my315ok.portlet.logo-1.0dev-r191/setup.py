from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='my315ok.portlet.logo',
      version=version,
      description="a portlet for customize site logo",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='logo portlet',
      author='adam tang',
      author_email='yuejun.tang@gmail.com',
      url='http://315ok.org',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['my315ok', 'my315ok.portlet'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
