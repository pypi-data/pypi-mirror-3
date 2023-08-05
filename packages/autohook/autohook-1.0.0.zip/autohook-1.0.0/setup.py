# -*- coding: utf-8 -*- 
from setuptools import setup


setup(
    name = "autohook",
    version = "1.0.0",
    packages = ['autohook'],
    # metadata
    author = u"Fredrik Håård",
    author_email = "fredrik@haard.se",
    description = "Automatic hook configuration for multiple Mercurial repositories",
    license = "Do whatever you want, don't blame me",
    keywords = "mercurial hook api",
    url = "https://bitbucket.org/haard/autohook",
    long_description = """
Can be configured in any hgrc (system, user, repo) and trigger for 
a push (pretxnchangegroup) into any repository that uses that hgrc. 
Can load external (Python) hooks that needs to accept parameters 
repo, user, start revison, end revision

Contains two built-in hooks, adds_branch and has_multiple_heads, 
and users that can bypass hooks can be defined. Depends on hgapi (https://bitbucket.org/haard/hgapi).
"""
)
