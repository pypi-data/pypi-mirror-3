from setuptools import setup, find_packages
import os

version = open(os.path.join("collective", "wfform", "version.txt")).read().strip()

setup(name='collective.wfform',
      version=version,
      description="",
      long_description=open(os.path.join("README.txt")).read() + "\n" +
                       open(os.path.join("docs", "INSTALL.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Michael Davis',
      author_email='m.r.davis@cranfield.ac.uk',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'z3c.form',
          'plone.app.registry',
          'plone.app.z3cform',
      ],
      extras_require = {
            'test': [
                    'plone.app.testing',
                ]
      },
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
)
