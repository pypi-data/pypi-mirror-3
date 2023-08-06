# -*- coding: utf-8 -*-
from distutils.core import setup
cmdclass = {}
try:
    from distutils.command.build_py import build_py_2to3
    cmdclass['build_py'] = build_py_2to3
except ImportError:
    pass
try:
    from sphinx.setup_command import BuildDoc
    cmdclass['build_sphinx'] = BuildDoc
except ImportError:
    pass
try:
    # Use local copy of upload_docs, to avoid importing setuptools
    from upload_docs import upload_docs
    cmdclass['upload_docs'] = upload_docs
except (ImportError, SyntaxError):
    pass

version='1.12'
setup(name='openid2rp',
      version=version,
      description='OpenID 2.0 Relying Party Support Library with WSGI and Django support',
      license = 'Academic Free License, version 3',
      author='Martin v. Loewis',
      author_email='martin@v.loewis.de',
      long_description=open('README').read(),
      url='http://pypi.python.org/pypi/openid2rp',
      download_url='http://pypi.python.org/packages/source/o/openid2rp/openid2rp-%s.tar.gz' % version,
      classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Academic Free License (AFL)",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        ],
      packages=['openid2rp','openid2rp.django', 'openid2rp.wsgi'],
      cmdclass = cmdclass
      )
