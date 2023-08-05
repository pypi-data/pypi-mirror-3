Summary
-------

The `comment` cube provides threadable comments feature.

It is a CubicWeb component. CubicWeb is a semantic web application
framework, see http://www.cubicweb.org


Install
-------

Auto-install from sources prefered with *pip/Distribute*::

  pip install cubicweb-comment

If you have troubles, use *easy_install/setuptools* and eggs::

  easy_install cubicweb-comment

You can install the package manually from the uncompressed
`tarball <http://www.cubicweb.org/project/cubicweb-comment>`_::

  python setup.py install # auto-install dependencies

If you don't want the dependancies to be installed automaticly, you
can force the setup to use the standard library *distutils*::

  NO_SETUPTOOLS=1 python setup.py install

More details at http://www.cubicweb.org/doc/en/admin/setup

Usage
-----

This cube creates a new entity type called `Comment` which could basically be
read by every body but only added by application's users.
It also defines a relation `comments` which provides the ability to add a
`Comment` which `comments` a `Comment`.

To use this cube, you want to add the relation `comments` on the entity type
you want to be able to comment. For instance, let's say your cube defines a
schema for a blog. You want all the blog entries to be commentable.
Here is how to define it in your schema:

.. sourcecode:: python

    from yams.buildobjs import RelationDefinition
    class comments(RelationDefinition):
        subject = 'Comment'
        object = 'BlogEntry'
        cardinality = '1*'

Once this relation is defined, you can post comments and view threadable
comments automatically on blog entry's primary view.

Documentation
-------------

Look in the ``doc/`` subdirectory or read
http://www.cubicweb.org/doc/en/
