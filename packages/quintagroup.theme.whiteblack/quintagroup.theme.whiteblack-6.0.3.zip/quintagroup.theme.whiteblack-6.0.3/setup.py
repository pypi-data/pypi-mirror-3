from setuptools import setup, find_packages
import os

version = '6.0.3'

setup(name='quintagroup.theme.whiteblack',
      version=version,
      description="Free Diazo Theme for Plone 4.1",
      long_description=open(os.path.join("quintagroup", "theme", "whiteblack", "README.txt")).read() + "\n\n" +
                       open(os.path.join("docs", "INSTALL.txt")).read() + "\n\n"+
                       open(os.path.join("docs", "HISTORY.txt")).read(),
                       
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='web zope plone diazo theme quintagroup',
      author='Quintagroup',
      author_email='skins@quintagroup.com',
      url='http://skins.quintagroup.com/whiteblack',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['quintagroup', 'quintagroup.theme',],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'plone.app.theming',
                        ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
