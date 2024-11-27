Using the Command Line Interface (CLI)
======================================

The NWBInspector tool offers convenient command-line usage via any standard Conda or Python terminal.

You may then run the NWBInspector via the command line via the following usages

::

    # supply a path to a single NWBFile
    nwbinspector path/to/my/data.nwb

    # supply a path to a directory containing several NWBFiles (this will recurse to subdirectories)
    nwbinspector path/to/my/data/dir/


which should quickly display a basic report to your console window.


All available options for the CLI may be viewed by calling ``nwbinspector --help``. We will now highlight some of
the most useful of these options.



Streaming
---------

If the NWB file(s) you wish to inspect are already on the :dandi-archive:`DANDI archive <>`, you can run the NWB Inspector directly on that DANDI set instead of having to download it.

To use this feature, some additional dependencies must be installed using:

.. code-block:: bash

    pip install "nwbinspector[dandi]"


Then, all that is needed is to specify the DANDI set ID (six-digit identifier) as the path and add the ``--stream`` flag.

::

    nwbinspector 000017 --stream

.. note::

    The default configuration becomes ``"dandi"`` when streaming contents on the archive.



Formatting the Report
---------------------

The basic report layout organizes by :py:attr:`~nwbinspector.register_checks.InspectorMessage.importance` first and
:py:attr:`~nwbinspector.register_checks.InspectorMessage.file_path` last.

However, the NWBInspector supports more general organization as defined by the ``--levels`` flag. To use this flag,
you must pass a series a comma-separated words that correspond to any attributes of the
:py:class:`~nwbinspector.register_checks.InspectorMessage` in any order.

For example,

::

    nwbinspector path/to/my/data/dir/ --levels check_function_name,object_type,file_path

.. note::

    The :py:attr:`~nwbinspector.register_checks.InspectorMessage.message` itself cannot be used in organization.

The ascending or descending order of each of these levels may be additionally controlled with the ``--reverse`` flag,
which is likewise a comma-separated series of boolean words.

For example,

::

    nwbinspector path/to/my/data/dir/ --levels check_function_name,object_type,file_path --reverse false,true,false

.. note::

    Valid 'boolean words' are any capitalizations of the words ``"false", "true"`` or characters ``"F", "T"``, and even
    numbers like ``"0, 1"``.


The default report also aggregates identical outputs into a summary over multiple files; running

::

    nwbinspector 000017 --stream

gives an output containing

.. image:: ../images/example_file_path_aggregation.png

as an example. It will do this any time the last value of the ``--levels`` list is ``file_path``. To see the full report of every
issue over all files, use the ``--detailed`` flag.



Saving the Report
-----------------

There are many common options you can specify with flags, such as saving the report for future reference...

::

    nwbinspector path/to/my/data.nwb --report-file-path path/to/my/nwbinspector_report.txt


If a report file from a previous run of the inspector is already present at the location, it can be overwritten with
the ``-o`` or ``--overwrite`` flag...

::

    nwbinspector path/to/my/data.nwb --report-file-path path/to/my/nwbinspector_report.txt -o



Faster Inspection
-----------------

The NWBInspector supports parallelization over a directory to allow the NWBInspector to run many times faster. To use
this feature, simply set the ``--n-jobs`` flag to either a positive integer corresponding to the number of CPUs you
wish to use, or set to ``-1`` to use all available system resources.

For example,

::

    nwbinspector path/to/my/data/dir/ --n-jobs -1



External Modules
----------------

If the NWB files being inspected have externally defined check registries, such as any specific Best Practices for an :ref:`NWB Extension <nwb-schema:sec-extending-the-format>`, these can be loaded using the ``--modules`` flag along with the name of each module spelled exactly as you would normally import it in Python. If there is more than one such module, multiple modules would be comma-separated without a space.

For example,

::

    nwbinspector path/to/my/data.nwb --modules my_extension_module1,my_extension_module2
