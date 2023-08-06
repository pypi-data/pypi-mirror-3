from setuptools import setup
from setuptools.extension import Extension

ext_modules = [Extension("ioctl_requests", ["ioctl_requests.c"])]

setup(
  name = 'intinfo',
  description = 'Its hard to get network interface information in python in a portable manner. This should help, at least in *nix environments.',
  version = '0.1',
  license = 'GPL v3',
  author = 'Ben Toews (mastahyeti)',
  author_email = 'mastahyeti@gmail.com',
  url = 'http://github.com/mastahyeti/intinfo',
  ext_modules = ext_modules,
  py_modules = ['intinfo'],
)