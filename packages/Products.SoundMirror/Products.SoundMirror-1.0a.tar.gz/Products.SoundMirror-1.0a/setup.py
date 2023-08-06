from setuptools import setup, find_packages
import os

version = '1.0a'

setup(name='Products.SoundMirror',
      version=version,
      description="A product that enables uploading an audio file that reflects the content of the object",
      long_description=open(os.path.join("Products", "SoundMirror", "readme.txt")).read() +\
          open(os.path.join("Products", "SoundMirror", "changes.txt")).read(),
                       
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        ],
      keywords='python plone archetypes accessibility sound media',
      author='Morten W. Petersen',
      author_email='info@nidelven-it.no',
      url='http://www.nidelven-it.no/d',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.PatchPloneContent>=1.0.3',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
