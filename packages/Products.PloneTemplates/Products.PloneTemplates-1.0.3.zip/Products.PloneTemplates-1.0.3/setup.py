from setuptools import setup, find_packages

version = '1.0.3'

setup(name='Products.PloneTemplates',
      version=version,
      description='Content templates for Plone',
      long_description=open('README.txt').read() + '\n' +
                       open('CHANGES.txt').read(),
      author='Danny Bloemendaal',
      author_email='danny.bloemendaal@informaat.nl',
      classifiers=[
          'Programming Language :: Python',
          'Framework :: Zope2',
          'Framework :: Plone',
      ],
      keywords='Zope Plone Templates', 
      license='ZPL',
      url='http://pypi.python.org/pypi/Products.PloneTemplates',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
      ],
      )
