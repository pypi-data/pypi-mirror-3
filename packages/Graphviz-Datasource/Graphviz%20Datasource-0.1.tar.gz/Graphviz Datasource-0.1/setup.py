#!/usr/bin/env python

from distutils.core import setup

setup(name='Graphviz Datasource',
      version='0.1',
      description="Datasource for google graphviz",
      author="Josh Frederick",
      author_email="josh@jfred.net",
      url="https://bitbucket.org/jfred/py-gvizds",
      packages=[
          "gvizds",
      ],
      install_requires=[
          "pyparsing",
          "eventlet",
          "nudge",
      ],
)
