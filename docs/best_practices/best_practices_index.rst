Best Practices
==============

The goal of the following document is to provide users of the NWB standard with additional guidelines on common best practices to
facilitate consistent use of the standard and help avoid common problems and most effectively leverage the NWB data standard
and its ecosystem of software tools.

To enable NWB to accommodate the needs of the diverse neuroscience community, NWB provides a great degree of flexibility.
In particular, the number of instances of a particular neurodata_type and corresponding names are often not fixed, to enable,
e.g., storage of data from arbitrary numbers of devices within the same file. While this flexibility is essential to enable
coverage of a broad range of use-cases, it can also lead to ambiguity. At the same time, we ultimately have the desire to have
the schema as strict-as-possible to provide users and tool builders with a consistent organization of data. As such, we need to
strike a fine balance between flexibility to enable support for varying experiments and use-cases and strictness in the schema
to enforce standard organization of data. The following “best practices” provide advice from developers and experienced users
that outline some of the pitfalls to avoid and common usage patterns to emulate.

Authors: Oliver Ruebel, Andrew Tritt, Ryan Ly, Cody Baker and Ben Dichter


.. toctree::
   :maxdepth: 2

   general
   nwbfile_metadata
   time_series
   tables
   behavior
   ecephys
   ophys
   ogen
   image_series
   images
   simulated_data
   extensions
