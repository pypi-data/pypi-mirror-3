from setuptools import setup, find_packages

version = '0.5'

setup(name='xm.charting',
      version=version,
      description="For generating gantt charts",
      long_description=(open("README.txt").read() + "\n" +
                        open("CHANGES.rst").read()),
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Plone",
          "Framework :: Zope2",
          "Framework :: Zope3",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      keywords='',
      author='Rocky Burt',
      author_email='rocky@serverzen.com',
      url='https://plone.org/products/extreme-management-tool/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['xm'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.eXtremeManagement',
      ],
      test_suite='xm.charting.tests.test_suite',
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
