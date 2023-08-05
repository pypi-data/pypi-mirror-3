from setuptools import setup, find_packages

version = '4.3'

setup(name='Products.SimpleAttachment',
      version=version,
      description="Simple Attachments for Plone",
      long_description=open("README.txt").read() + '\n' +
            open('CHANGES.txt').read(),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        ],
      keywords='Plone attachments RichDocument',
      author='Martin Aspeli',
      author_email='',
      url='http://pypi.python.org/pypi/Products.SimpleAttachment',
      license='GPL',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'archetypes.schemaextender',
          'plone.app.blob',
      ],
      extras_require={ 'test': [
          'zope.testing',
          'collective.testcaselayer',
          'Products.RichDocument',
      ]},
      )
