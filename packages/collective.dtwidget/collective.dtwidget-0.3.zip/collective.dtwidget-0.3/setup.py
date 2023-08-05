from setuptools import setup, find_packages

version = '0.3'

setup(name='collective.dtwidget',
      version=version,
      description="Munges the ATDateTime CalendarWidget into a formlib widget.  Plone only",
      long_description=(
          open('README.txt').read() + '\n' +
          open('CHANGES.txt').read()
      ),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        ],
      keywords='formlib widget Datetime',
      author='Matthew Wilkes',
      author_email='matthew.wilkes@circulartriangle.eu',
      url='http://pypi.python.org/pypi/collective.dtwidget',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      )
