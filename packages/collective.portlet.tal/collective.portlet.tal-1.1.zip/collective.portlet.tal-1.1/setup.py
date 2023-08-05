from setuptools import setup, find_packages

version = '1.1'

setup(name='collective.portlet.tal',
      version=version,
      description="TAL portlet for Plone 3 and 4",
      long_description="""\
This portlet allows you to enter TAL into a text area, which is then executed
as if it came from a page template""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone portlet tal',
      author='Martin Aspeli',
      author_email='optilude@gmx.net',
      url='http://plone.org',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.portlet'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.CMFPlone',
          'Products.PloneTestCase',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
