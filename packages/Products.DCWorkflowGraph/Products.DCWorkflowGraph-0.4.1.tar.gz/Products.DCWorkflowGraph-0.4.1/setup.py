from setuptools import setup, find_packages
import os

version = '0.4.1'

setup(name='Products.DCWorkflowGraph',
      version=version,
      description="DCWorkflowGraph is a DCWorkflow graphic viewer now. It uses Graphviz.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Author: panjunyong (panjy at zopen.cn, from ZOpen)',
      author_email='panjy at zopen.cn',
      url='http://svn.plone.org/svn/collective/Products.DCWorkflowGraph/',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [distutils.setup_keywords]
      paster_plugins = setuptools.dist:assert_string_list

      [egg_info.writers]
      paster_plugins.txt = setuptools.command.egg_info:write_arg
      """,
      paster_plugins = ["ZopeSkel"],
      )
