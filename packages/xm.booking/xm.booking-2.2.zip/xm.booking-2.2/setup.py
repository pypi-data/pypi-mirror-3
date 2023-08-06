from setuptools import setup, find_packages

readmefile = open('README.txt')
readme = readmefile.read().strip()
readmefile.close()

historyfile = open('CHANGES.rst')
history = historyfile.read().strip()
historyfile.close()

setup(name='xm.booking',
      version='2.2',
      description="Bookings for eXtremeManagement",
      long_description=readme + "\n\n" + history,
      classifiers=[
          "Framework :: Plone",
          "Framework :: Zope2",
          "Framework :: Zope3",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      keywords='eXtremeManagement booking',
      author='Maurits van Rees',
      author_email='m.van.rees@zestsoftware.nl',
      url="http://plone.org/products/extreme-management-tool/",
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['xm'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.indexer',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
