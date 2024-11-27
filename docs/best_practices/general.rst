General
=======



Neurodata Types
---------------



.. _best_practice_object_names:

Naming Conventions
~~~~~~~~~~~~~~~~~~

As a default, name class instances with the same name as the class. If appropriate, simply use the name of the
``neurodata_type`` as the name of that object. *E.g.*, if your :ref:`nwb-schema:sec-NWBFile` has only a single
:ref:`nwb-schema:sec-ElectricalSeries` that holds voltage traces for a multichannel recording, then simply name it
``ElectricalSeries``.

There may be cases where you have multiple instances of the same ``neurodata_type`` in the same Group. In this case,
the instances must have unique names. An easy way to achieve this is to add an index or other minimal distinguishing
characteristics to the end of the name of that ``neurodata_type``; an example for multiple
:ref:`nwb-schema:sec-ElectricalSeries` (corresponding perhaps to differing segments or electrode regions) might be to
distinguish them as ``ElectricalSeries1`` and ``ElectricalSeries2``, or as ``ElectricalSeries`` and
``ElectricalSeriesExtraElectrodes``.

Following this practice allows multiple objects of the same type to be stored side-by-side and increase your chances
that analysis and visualization tools will operate seamlessly to provide human-readable information about the contents
of the file.

It is recommended to use :wikipedia:`CamelCase <Camel_case>` when naming instances of schematic classes.



.. _best_practice_name_slashes:

Do Not Use Slashes in Names
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Slash characters ``'/'`` and ``'\'``  should not be used in the ``name`` of an object, because they can be confusing to systems that parse HDF5 files (which NWB uses as the primary backend, see the :nwb-overview:`NWB FAQ <faq_details/why_hdf5.html#why-hdf5>` for more details). The forward slash is used in `h5py` to specify a `Groups <https://schema-language.readthedocs.io/en/latest/description.html#groups>`_ hierarchy.

For mathematical expressions, instead of including the special character in the name, please use an English equivalent instead. *E.g.*, instead of "Df/f" use "DfOverF".

Check function: :py:meth:`~nwbinspector.checks._general.check_name_slashes`



.. _best_practice_description:

Descriptions
~~~~~~~~~~~~

The :py:attr:`name` of an object is for identifying that object within the file; it is not for storing metadata. Instead, the :py:attr:`description` field for most objects can be used to include any important distinguishing information. When writing metadata, be as explicit and self-contained as possible in explaining relevant details. Use official ontologies where appropriate.

It is acceptable to name an object something like ``ElectricalSeriesFromProbe1`` as per the uniqueness requirement of :ref:`best_practice_object_names`, however the name alone is not sufficient documentation of the signal source. In this case, the source of the signal will be clear from the :ref:`nwb-schema:devices` linkage in the rows of the passed :ref:`hdmf-schema:sec-dynamictableregion` subsetting the full ``ElectrodeTable``, so you would not need to add any explicit metadata explaining these details.

Check function: :py:meth:`~nwbinspector.checks._general.check_description`




.. _best_practice_placeholders:

Empty Strings
~~~~~~~~~~~~~

Required free-text fields for neurodata types should not use placeholders such as empty strings (`""`), ``"no description"``, or ``"PLACEHOLDER"``. For example, the :py:attr:`description` field should always richly describe that particular neurodata type and its interpretation within the experiment.

Many attributes of neurodata types in NWB are optional details to include. It is not necessary, therefore, to use placeholders for these attributes. Instead, they should not be specified at all.


Avoid Duplication of Metadata
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Avoid duplication of metadata across different objects. If a piece of metadata is shared between multiple objects, consider creating a separate object to store that metadata and linking to it from the other objects. This will help to keep the metadata consistent and reduce the risk of errors when updating the metadata.
