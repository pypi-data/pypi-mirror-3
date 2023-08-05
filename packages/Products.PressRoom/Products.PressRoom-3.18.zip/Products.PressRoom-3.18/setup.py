from setuptools import setup, find_packages

version = '3.18'

setup(name='Products.PressRoom',
      version=version,
      description="Allows users to instantly create a polished, professional "
                  "press room, featuring press releases, press clips and press "
                  "contacts.  Manage an online Press Room within your Plone "
                  "site.",
      long_description=open("README.txt").read() + "\n" +
                       open("CREDITS.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Development Status :: 6 - Mature",
        ],
      keywords='plone press media news release',
      author='Groundwire',
      author_email='info@groundwire.org',
      url='http://plone.org/products/pressroom',
      license='GPL',
      packages=find_packages(),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      )
