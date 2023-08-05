import os

from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.3'
long_description = """
%s

%s
""" % (read("README.txt"),
       read("docs", "CHANGES.txt"))


setup(name='p4a.plonevideoembed',
      version=version,
      description="Plone4Artists video embedding add-on for Plone",
      long_description=long_description,
      classifiers=[
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Video",
        ],
      keywords='video youtube Plone4Artists',
      author='Rocky Burt',
      author_email='rocky@serverzen.com',
      url='http://plone.org/products/plone4artistsvideo',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['p4a'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'p4a.video>1.3',
          'p4a.videoembed>1.2',
          'Products.fatsyndication',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
