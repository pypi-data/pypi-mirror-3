Summary
-------
The `blog` cube provides blogging functionnalities. It creates two entity types,
`Blog` and `BlogEntry`. There are related to each other by the relation
`BlogEntry entry_of Blog`.

It is a CubicWeb component. CubicWeb is a semantic web application
framework, see http://www.cubicweb.org

Install
-------

Auto-install from sources prefered with *pip/Distribute*::

  pip install cubicweb-blog

If you have troubles, use *easy_install/setuptools* and eggs::

  easy_install cubicweb-blog

You can install the package manually from the uncompressed
`tarball <http://www.cubicweb.org/project/cubicweb-blog>`_::

  python setup.py install # auto-install dependencies

If you don't want the dependancies to be installed automaticly, you
can force the setup to use the standard library *distutils*::

  NO_SETUPTOOLS=1 python setup.py install

More details at http://www.cubicweb.org/doc/en/admin/setup

Usage
-----

When a user submits a blog entry, it goes in a `draft` state until the blog
entry is published by an application managers. The blog entry will not be
visible until it reaches the `published` state.

When a blog entry is submitted, an email notification is automatically sent
to all the users belonging to the `managers` group of the application.

Specific boxes provided by this cube:

- `BlogEntryArchiveBox`, displays a box with the total number of blog entries
  submitted by month for the last twelve months.

- `BlogEntryListBox`, displays a box with the latest five blog entries
  published in your application as well as link to subscribe to a RSS feed.

- `BlogEntrySummary`, displays a box with the list of users who submitted
  blog entries and the total number of blog entries they submitted.

This cube also provides some web services such as:

- http://xx:xxxx/blogentries/YYYY to retrieve the blog entries submitted
  during the year YYYY through a RSS feed

- http://xx:xxxx/blogentries/YYYY/MM to retrieve the blog entries submitted
  during the month MM of the year YYYY through a RSS feed

- http://xx:xxxx/blog/[eid]/blogentries/YYYY to retrieve the blog entries
  submitted in the blog of identifier [eid], during the year YYYY through
  a RSS feed

- http://xx:xxxx/blog/[eid]/blogentries/YYYY/MM to retrieve the blog entries
  submitted in the blog of identifier [eid], during the month MM of the
  year YYYY through a RSS feed

Documentation
-------------

Look in the ``doc/`` subdirectory or read
http://www.cubicweb.org/doc/en/
