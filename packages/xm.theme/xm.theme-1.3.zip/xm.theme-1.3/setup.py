from setuptools import setup, find_packages

setup(name='xm.theme',
      version='1.3',
      description="Theme for eXtremeManagement",
      long_description=open('CHANGES.rst').read(),
      classifiers=[
          "Framework :: Plone",
          "Framework :: Zope2",
          "Framework :: Zope3",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      keywords='web zope plone theme',
      author='Zest Software',
      author_email='info@zestsoftware.nl',
      url='http://zestsoftware.nl',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['xm'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.eXtremeManagement>=2.0alpha3',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
