from setuptools import setup, find_packages
import os.path

version = '1.0'

setup(name='plonerelations.ATField',
      version=version,
      description="ATField for plone.relations",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("plonerelations", "ATField", "ploneRelationsATField.txt")).read() + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone.relation field widget archetypes',
      author='Alec Mitchell, Mika Tasich',
      author_email='apm13@columbia.edu',
      url='http://pypi.python.org/pypi/plonerelations.ATField',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plonerelations'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.relations',
      ],
      )
