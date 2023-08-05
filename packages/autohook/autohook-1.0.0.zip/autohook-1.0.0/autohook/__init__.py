"""
sample config
[hooks]
pretxnchangegroup = python:path/to/autohook/autohook.py:hook

[autohook]
debug=True
loadpath=/path/to/hooks
loadmodules=hookmodule1 hookmodule2
tests = adds_branch hookmodule1.myhook
repos = orig
orig.path = /path/to/repo
orig.tests = has_multiple_heads hookmodule2.hook

""" 
