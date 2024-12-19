Using the Library
=================

For users familiar with Python, our core functions may also be used directly to allow greater freedom in handling input
and output.



InspectorMesssage objects
-------------------------

In order to understand the output of the core functions, we must first explain the most important data structure in our
library, the :py:class:`~nwbinspector.register_checks.InspectorMessage`. This is a standalone data class that contains
all values that could be useful or related to a detected Best Practice issue. These values include the text-based
``message`` displayed in the report, the ``importance`` of the check (how crucial it is to fix), the ``object_name``
and ``object_type`` that triggered the issue, the ``location`` of that object within the NWB file, and the ``file_path``
of the NWBFile relative to the directory the inspection function was called from.



Inspect a single NWBFile
------------------------

The most basic function to use when inspecting a single NWB file is the
:py:class:`~nwbinspector.nwbinspector.inspect_nwbfile` function.

.. code-block:: python

    from nwbinspector import inspect_nwbfile

    results = list(inspect_nwbfile(nwbfile_path="path_to_single_nwbfile"))

This returns a ``list`` of :py:class:`~nwbinspector.register_checks.InspectorMessage` objects.

If you have an :py:class:`~pynwb.file.NWBFile` object in memory, you can run

.. code-block:: python

    from nwbinspector import inspect_nwbfile_object
    from pynwb import NWBHDF5IO

    with NWBHDF5IO(path="path_to_single_nwbfile", mode="r", load_namespaces=True) as io:
        nwbfile = io.read()
        messages = list(inspect_nwbfile_object(nwbfile))

This approach can be used to inspect a Zarr :py:class:`~pynwb.file.NWBFile` as well

.. code-block:: python

    from hdmf_zarr.nwb import NWBZarrIO

    with NWBZarrIO("example_zarr.nwb", "r") as zarr_io:
        nwbfile = zarr_io.read()
        messages = list(inspect_nwbfile_object(nwbfile))

Inspect a Directory or List of Paths to NWBFiles
------------------------------------------------

If you want to run essentially the same code as the CLI, use the :py:class:`~nwbinspector.nwbinspector.inspect_all`
function.

.. code-block:: python

    from nwbinspector import inspect_all

    all_results = list(inspect_all(path=file_paths_or_folder, ...))

This has the same return structure as :py:class:`~nwbinspector.nwbinspector.inspect_nwbfile`.


.. note::

    For convenience, all path-based arguments in the NWBInspector library support both ``str`` and ``pathlib.Path`` types.



.. _simple_streaming_api:

Inspect a Dandiset
------------------

It is a common use case to inspect and review entire datasets of NWB files that have already been uploaded to the
:dandi-archive:`DANDI Archive <>`. While it is possible to simply download the entire dandiset to your local computer and
run the NWB Inspector as usual, it can be more convenient to stream the data. This can be especially useful when the
dandiset is large and impractical to download in full.

Begin by installing the dependencies for streaming:

.. code-block:: bash

    pip install "nwbinspector[dandi]"

Then, you can use the :py:meth:`~nwbinspector.inspect_dandiset` function to stream the data from the DANDI

.. code-block:: python

    from nwbinspector import inspect_dandiset

    dandiset_id = "000004"

    messages = list(inspect_dandiset(dandiset_id=dandiset_id))

If there are multiple versions of the dandiset available (*e.g.*, separate 'draft' and 'published' versions) you can
additionally specify this with the ``dandiset_version`` argument.

.. code-block:: python

    from nwbinspector import inspect_dandiset

    dandiset_id = "000004"
    dandiset_version = "0.220126.1851"

    messages = list(inspect_dandiset(dandiset_id=dandiset_id, dandiset_version=dandiset_version))

See the section on :ref:`advanced_streaming_api` for more customized usage of the streaming feature.



Examining the Default Check Registry
------------------------------------

While it does not need to be imported directly for default usage, an interested user may inspect the ``list`` of all
available check functions via

.. code-block:: python

    from nwbinspector import available_checks
