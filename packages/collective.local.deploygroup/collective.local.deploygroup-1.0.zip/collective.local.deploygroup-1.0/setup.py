from setuptools import setup, find_packages

version = '1.0'

setup(name='collective.local.deploygroup',
      version=version,
      description="Allows to deploy a group from the sharing view. By Ecreall",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Vincent Fretin',
      author_email='vincent.fretin@gmail.com',
      url='http://svn.plone.org/svn/collective/collective.local.deploygroup',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.local'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.workflow',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
