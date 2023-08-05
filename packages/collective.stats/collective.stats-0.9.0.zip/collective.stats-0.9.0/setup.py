import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.9.0'


setup(name='collective.stats',
      version=version,
      description="Zope low level stats per request.",
      long_description=open('README.rst').read() + open(os.path.join('docs', 'HISTORY.txt')).read(),
      classifiers=[
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      author='Enfold Systems',
      author_email='contact@enfoldsystems.com',
      maintainer='Alex Clark',
      maintainer_email='aclark@aclark.net',
      url='http://github.com/collective/collective.stats',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'ZODB3',
          'Zope2',
          'psutil',
      ],
      extras_require = dict(
        oldzope=['ZPublisherEventsBackport']),
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      
      [console_scripts]
      collective-stats = collective.stats.export:main
      """,
      )
