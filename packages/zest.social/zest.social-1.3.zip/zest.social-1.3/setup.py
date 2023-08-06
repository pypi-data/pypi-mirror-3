from setuptools import setup, find_packages

version = '1.3'

setup(name='zest.social',
      version=version,
      description="Zest Social Bookmarking",
      long_description=(open("README.txt").read() + "\n" +
                        open("CHANGES.rst").read()),
      classifiers=[
          "Framework :: Plone",
          "Framework :: Plone :: 3.3",
          "Framework :: Plone :: 4.0",
          "Framework :: Plone :: 4.1",
          "Framework :: Plone :: 4.2",
          "Programming Language :: Python",
          ],
      keywords='social bookmarking addthis',
      author='Zest Software',
      author_email='info@zestsoftware.nl',
      url='https://github.com/zestsoftware/zest.social',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zest'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'archetypes.schemaextender',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
