from setuptools import setup, find_packages

version = '1.0'

setup(name='Products.Zope_Hotfix_CVE_2011_3587',
      version=version,
      description="Hotfix to fix CVE 2011-3587 for Zope 2.12 + 2.13",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Zope2",
        "License :: OSI Approved :: Zope Public License",
        ],
      keywords='security hotfix patch',
      author='Zope Foundation and Contributors',
      author_email='zope-dev@zope.org',
      url='http://svn.zope.org/Zope/hotfixes/Products.Zope_Hotfix_CVE_2011_3587',
      license='ZPL 2.1',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      )
