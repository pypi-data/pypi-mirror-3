from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='ngi.site.notification',
      version=version,
      description="Changing a Plone content  into a designated state, tweets in Twitter.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='Plone',
      author='Takashi NAGAI',
      author_email='nagai@ngi644.net',
      url='http://ngi644.net',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ngi', 'ngi.site'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.dexterity',
          'plone.app.registry',
          'python-twitter',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
