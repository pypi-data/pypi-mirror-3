from setuptools import find_packages
from setuptools import setup

version = '1.0'

ZSVN = 'http://svn.zope.org/Zope/'

setup(name='Products.Zope_Hotfix_CVE_2010_1104',
      version=version,
      description="Hotfix to fix CVE 2010-1104 for Zope 2.8 - 2.13",
      long_description=open("README.txt").read(),
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Zope2",
        "License :: OSI Approved :: Zope Public License",
      ],
      keywords='security hotfix patch',
      author='Zope Foundation and Contributors',
      author_email='zope-dev@zope.org',
      url=ZSVN + 'hotfixes/Products.Zope_Hotfix_CVE_2010_1104',
      license='ZPL 2.1',
      packages=find_packages(),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
)
