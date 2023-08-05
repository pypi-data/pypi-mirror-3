Faculty Staff Directory: Core
=============================

.. _FacultyStaffDirectory: http://pypi.python.org/pypi/Products.FacultyStaffDirectory
.. _fsd.classic: http://pypi.python.org/pypi/fsd.classic

Faculty Staff Directory is a personnel directory that provides a way of
creating and grouping personnel.

This package is a part of the next generation `FacultyStaffDirectory`_. It
will only work with Plone 4.1 and greater.

The ``fsd.core`` package provides three types of content: Person,
Group and Person Group Data. The Person and Group content-types makes up the
majority of the functionality required to build a rudimentary personnel
directory.

The Person Group Data content-type is used to provide metadata
about the Person to Group relationship (e.g. Affiliation -> 'President',
Title -> 'Store Manager'). This content-type is not directly addable through
the Plone interface. Group data can only be applied through the Person or Group
edit forms.

The provided content-types of purposely lean to increase the reusability of the types. The `fsd.classic`_ package can be used to add common personnel fields (and fields commonly found in `FacultyStaffDirectory`_) to the Person content-type.
