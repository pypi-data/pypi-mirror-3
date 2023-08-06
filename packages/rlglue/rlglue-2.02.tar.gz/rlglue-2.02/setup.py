#! /usr/bin/env python

from distutils.core import setup
from rlglue.versions import get_codec_version
import rlglue



setup(name="rlglue",
      version=get_codec_version(),
      description="RL-Glue Python Codec",
      author="Brian Tanner",
      author_email=" brian@tannerpages.com",
      url="http://glue.rl-community.org/Home/Extensions/python-codec",
      download_url="http://rl-glue-ext.googlecode.com/files/python-codec-2.02.tar.gz",
      packages=['rlglue','rlglue.agent','rlglue.environment','rlglue.network','rlglue.utils'],
      license='Apache License Version 2.0',
      classifiers=[
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Operating System :: OS Independent",
        ],
      long_description="""\
Python RL-Glue Codec, a software library that provides socket-compatibility with the RL-Glue Reinforcement Learning software library.
"""
     )

