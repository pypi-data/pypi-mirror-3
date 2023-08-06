from setuptools import setup, find_packages
import os

version = '0.4'

if version == 'trunk':
    download_url = 'https://svn.plone.org/svn/collective/collective.portlet.contentleadimage/tags/%s/' % version,
else:
    download_url = 'https://svn.plone.org/svn/collective/collective.portlet.contentleadimage/trunk/'

setup(name='collective.portlet.contentleadimage',
      version=version,
      description="Collection portlet that shows contenteleadimages",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        ],
      keywords='',
      author='Ales Zabala Alava (Shagi)',
      author_email='shagi@gisa-elkartea.org',
      url='http://lagunak.gisa-elkartea.org/projects/plone-leadimage/',
      download_url=download_url,
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.portlet'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.portlet.collection',
          'collective.contentleadimage',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
