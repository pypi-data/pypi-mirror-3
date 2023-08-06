# Copyright (c) 2010 Hong MinHee <http://dahlia.kr/>
# 
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
import os.path
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from irclog.version import VERSION

try:
    _f = open(os.path.join(os.path.dirname(__file__), "doc", "index.rst"))
    long_description = _f.read()
    _f.close()
except IOError:
    long_description = None
else:
    del _f


setup(name="irclog",
      description="The web IRC loger view.",
      long_description=long_description,
      version=VERSION,
      url='http://irclog.rtfd.org/',
      author="Hong MinHee",
      author_email="minhee" "@" "dahlia.kr",
      packages=["irclog", "irclog.web"],
      package_data={"irclog.web": ["templates/*/*"]},
      install_requires=["chardet", "Jinja2"],
      extras_require={"doc": ["Sphinx"],
                      "prod-meinheld": ["meinheld"],
                      "prod-gevent": ["gevent"],
                      "prod-rocket": ["rocket"]},
      test_suite="irclog.tests.suite",
      classifiers=["Development Status :: 3 - Alpha",
                   "Intended Audience :: Developers",
                   "Intended Audience :: End Users/Desktop",
                   "License :: OSI Approved :: MIT License",
                   "Topic :: Communications :: Chat :: Internet Relay Chat",
                   "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
                   "Topic :: System :: Logging"],
      license="MIT License")

