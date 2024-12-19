Extensions
==========

Extend the core NWB schema only when necessary. Extensions are an essential mechanism to integrate
data with NWB that is otherwise not supported. However, we here need to consider that there are certain costs associated
with extensions, *e.g.*, cost of creating, supporting, documenting, and maintaining new extensions and effort for users
to use and learn already-created extensions. As such, users should attempt to use core ``neurodata_types`` or
pre-existing extensions before creating new ones. :ref:`hdmf-schema:sec-dynamictable`, which are used throughout the
NWB schema to store information about time intervals, electrodes, or spiking output, provide the ability to
dynamically add columns without the need for extensions, and can help avoid the need for custom extensions in many
cases.

If an extension is required, tutorials for the process may be found through the
:nwb-overview:`NWB Overview for Extensions <extensions_tutorial/extensions_tutorial_home.html>`.

It is also encouraged for extensions to contain their own check functions for their own best practices.
See the :ref:`adding_custom_checks` section of the Developer Guide for how to do this.



Use Existing Neurodata Types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When possible, use existing types when creating extensions either by creating new ``neurodata_types`` that inherit from
existing ones, or by creating ``neurodata_types`` that contain existing ones. Building on existing types facilitates the
reuse of existing functionality and interpretation of the data. If a community extension already exists that has a
similar scope, it is preferable to use that extension rather than creating a new one.


Provide Documentation
~~~~~~~~~~~~~~~~~~~~~

When creating extensions be sure to provide thorough, meaningful documentation as part of the extension specification.
Explain all fields (groups, datasets, attributes, links etc.) and describe what they store and how they
should be used.


Write the Specification to the NWBFile
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can store the specification (core and extension) within the NWBFile through caching.
Caching the specification is preferable, particularly if you are using a custom extension, because this ensures that
anybody who receives the data also receives the necessary data to interpret it.

.. note::
    In :pynwb-docs:`PyNWB <>`, the extension is cached automatically. This can be specified explicitly with
    ``io.write(filepath, cache_spec=True)``
