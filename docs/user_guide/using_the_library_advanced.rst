Using the Library: Advanced
===========================

This is a collection of tutorials illustrating some of the more advanced uses of the NWBInspector


Yielding and Iterating
----------------------

Both the :py:class:`~nwbinspector.nwbinspector.inspect_all` and :py:class:`~nwbinspector.nwbinspector.inspect_nwbfile`
functions return generators. That is, they do not actually run any checks on any NWBFile until the user
performs an iteration command on them. The simplest way of doing this is to cast the generator as a ``list``,
*i.e.*, ``list(inspect_nwbfile(...))`` which will automatically complete all checks.

However, if a user chooses, they can harness these generators in more sophisticated ways. If you want to stop the
checks early, the following will run the inspectors until the first
:py:class:`~nwbinspector.register_checks.InspectorMessage` is returned:

.. code-block:: python

    results_generator = inspect_nwbfile(nwbfile_path="path_to_single_nwbfile")

    first_message = next(results_generator)

This will return either the first :py:class:`~nwbinspector.register_checks.InspectorMessage`, or it will raise a
``StopIteration`` error. This error can be caught in the following manner

.. code-block:: python

    results_generator = inspect_nwbfile(nwbfile_path="path_to_single_nwbfile")

    try:
        first_message = next(results_generator)
    except StopIteration:
        print("There are no messages!")

Of course, the generator can be treated like any other iterable as well, such as with :code:`for` loops

.. code-block:: python

    results_generator = inspect_nwbfile(nwbfile_path="path_to_single_nwbfile")

    for message in results_generator:
        print(message)



.. _advanced_streaming_api:

Fetching and inspecting individual DANDI assets
-----------------------------------------------

While the section explaining :ref:`basic steaming of a dandiset <simple_streaming_api>` covered the simplest and most
convenient usage of the streaming feature applied to an entire Dandiset, you might want to inspect only a single file.

In this case, we will use the :py:meth:`nwbinspector.inspect_dandi_file_path` function.

.. code-block:: python

    from nwbinspector import inspect_dandi_file_path

    dandiset_id = "000004"
    dandi_file_path = "sub-P17HMH/sub-P17HMH_ses-20080501_ecephys+image.nwb"

    messages = list(inspect_dandi_file_path(dandi_file_path=dandi_file_path, dandiset_id=dandiset_id))

Just like :py:meth:`nwbinspector.inspect_dandiset`, this function accepts a ``dandiset_version``.

In case your NWB file is accessible via some other cloud URL, you can also use the :py:meth:`nwbinspector.inspect_url`
function.

.. code-block:: python

    from nwbinspector import inspect_url

    url = "https://dandiarchive.s3.amazonaws.com/blobs/3d7/39a/3d739ac0-10fb-41ef-80be-f1479cec44c0"

    messages = list(inspect_url(url=url))



Format Reports
--------------

Reports aggregate messages into a readable form.

.. code-block:: python

    from nwbinspector.inspector_tools import format_messages

    print("\n".join(format_messages(messages, levels=["importance", "file_path"])))

The `levels` argument can be altered to change the nesting structure of the report. Any combination and order
of :py:class:`~nwbinspector.register_checks.InspectorMessage` attributes can be utilized to produce a more easily
readable structure.
