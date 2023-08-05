from setuptools import setup, find_packages

version = '1.1'

setup(name='collective.contentgovernance',
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Jarn AS',
      author_email='info@jarn.com',
      url='http://pypi.python.org/pypi/collective.contentgovernance',
      license='GPL',
      packages=find_packages(),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.testing',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
