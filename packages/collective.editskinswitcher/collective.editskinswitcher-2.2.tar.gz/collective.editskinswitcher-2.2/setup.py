from setuptools import setup, find_packages
import os

versionfile = open(os.path.join('collective', 'editskinswitcher', 'version.txt'))
version = versionfile.read().strip()
versionfile.close()

readmefile = open(os.path.join('collective', 'editskinswitcher', 'README.txt'))
readme = readmefile.read().strip()
readmefile.close()

historyfile = open('CHANGES.txt')
history = historyfile.read().strip()
historyfile.close()

long_description = "%s\n\n\n%s" % (readme, history)

setup(name='collective.editskinswitcher',
      version=version,
      description="Switch to the edit skin for certain domains.""",
      long_description=long_description,
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Maurits van Rees',
      author_email='m.van.rees@zestsoftware.nl',
      url="http://svn.plone.org/svn/collective/collective.editskinswitcher",
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
