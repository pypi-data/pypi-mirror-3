===========================================
Secure FTP (SFTP) Extension for zc.buildout
===========================================

The zc.buildoutsftp package provides a zc.buildout extension that
provides support for SFTP.  To use it, simply provide the option::

  extensions = zc.buildoutsftp

in your buildout section. Then you can use sftp URLs for find-links or
index URLs.

An SFTP URL is similar to an FTP URL and is of the form::

  sftp://user:password@hostname:port/path

where the user name, password, and port are optional.  Here are some
examples:

The following URL accesses the path /distribution on download.zope.org::

  sftp://download.zope.org/distribution

The following URL accesses the path /distribution on download.zope.org
using the user id jim::

   sftp://jim@download.zope.org/distribution

The following URL accesses the path /distribution on download.zope.org
using the user id jim and password 123::

  sftp://jim:123@download.zope.org/distribution


The following url accesses the path /distribution on download.zope.org
using an ssh server running on port 1022::

  sftp://download.zope.org:1022/distribution

The buildout extension actually installs a urllib2 handler for the
"sftp" protocol.  This handler is actually setuptools specific because
it generates HTML directory listings, needed by setuptools and makes
no effort to make directory listings useful for anything else.
It is possible that, in the future, setuptools will provide it's own
extension mechanism for handling alternate protocols, in which case,
we might bypass the urllib2 extension mechanism.

SSH Compatibility
=================

The extension works with Open SSH on unix-based systems and PuTTY on
Windows.  Unless a password is given in the URL, private keys are
ontained from ssh agent (pagent on Windows).

Status and Change History
=========================

This package has been used for years on Linux and Mac OS X.  The
author doesn't use it on Windows, but, presumably, other people do.

0.9.0b1 (2012/06/29)
--------------------

Added support for:

- Global-configuration settings.

- Global known-hosts files.

- Host-specific ssh keys.

Added mock-based tests for unix-like systems.  Unfortunately, these
tests will fail for Windows and windows support, while present, is
untested.

0.6.1 (2010/03/17)
------------------

Fixed documentation typo.

0.6.0 (2009/06/22)
------------------

Added an unload entry point.  This is necessary so we don't hang when
the buildout process exits due to non-daemonic paramiko connection
threads.

0.5.0 (2008/12/08)
------------------

Added connection pooling. This speeds up multiple downloads from the
same server substantially.

Adjust the paramiko logging level relative to the buildout logging
level to make it less chatty.

0.4.0 (2007/12/6)
-----------------

Now reads user definitions from ~/.ssh/config, if possible.

0.3.2 (2007/03/22)
------------------

Fixed a serious bug that caused files to be downloaded incompletely.

0.3.1 (2007/03/22)
------------------

Fixed a serious bug that caused files read to be truncated to 0 bytes.

0.3 (2007/03/22)
----------------

Added debug logging to help diagnose problems.

Close transports after use to prevent leakage.

0.2.2
-----

Fixed a bug in handling multiple host keys for a given host.

0.2.1
-----

Fixed a bug in handling multiple user keys.

0.2
---

Added missing entry point.

Adjusted content-type information to work with setuptools.

0.1
---

Initial release
