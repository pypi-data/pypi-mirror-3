from setuptools import setup, find_packages
import os

version = '0.1b2'

setup(name='collective.installedpackages',
      version=version,
      description='Add-on for Plone to list all Python packages available to the running Python process, its versions'
        'and other information about them.',
      long_description=open(os.path.join('collective', 'installedpackages', 'README.txt')).read() + "\n" +
                       open(os.path.join('docs', 'HISTORY.txt')).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        'Programming Language :: Python',
        'Framework :: Plone',
        
        ],
      keywords='plone dexterity',
      author='Rafael Oliveira',
      author_email='rafaelbco@gmail.com',
      url='http://svn.plone.org/svn/collective/collective.installedpackages',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'z3c.autoinclude',
          'Products.CMFPlone',
          'yolk',
          'five.grok',
      ],
      extras_require = {
        'test': [
            'plone.app.testing',
        ]
      },      
      entry_points="""
      # -*- Entry points: -*-
      """,
)
