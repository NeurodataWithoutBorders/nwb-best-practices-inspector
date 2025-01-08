Time Series
===========

When using :ref:`nwb-schema:sec-TimeSeries` or any subtype
(*e.g.*, :ref:`nwb-schema:sec-ElectricalSeries`, :ref:`nwb-schema:sec-SpatialSeries`,
:ref:`nwb-schema:sec-ImageSeries`, etc.) please ensure the following practices are followed.




.. _best_practice_data_orientation:

Data Orientation
~~~~~~~~~~~~~~~~

For the ``data`` field of :ref:`nwb-schema:sec-TimeSeries`, the first dimension of the array should always be time.

Keep in mind that the dimensions are reversed in MatNWB, so in memory in MatNWB the time dimension must be last.

In PyNWB the order of the dimensions is the same in memory as on disk, so the time index should be first.

Check functions: :py:meth:`~nwbinspector.checks._time_series.check_data_orientation` and
:py:meth:`~nwbinspector.checks._time_series.check_timestamps_match_first_dimension`



.. _best_practice_unit_of_measurement:

Units of Measurement
~~~~~~~~~~~~~~~~~~~~

Time-related values should always in seconds. This includes ``rate`` (if applicable), which should should be in Hz.

Every :ref:`nwb-schema:sec-TimeSeries` instance has ``unit`` as an attribute, which is meant to indicate the unit of
measurement for that data, using the appropriate type from the
:wikipedia:`International System of Units (SI) <International_System_of_Units>`.

Check function: :py:meth:`~nwbinspector.checks._time_series.check_missing_unit`



.. _best_practice_time_series_global_time_reference:

Time Series: Time References
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``timestamps`` or ``rate`` of a :ref:`nwb-schema:sec-TimeSeries` should be in seconds with respect to
the global ``timestamps_reference_time`` of the :ref:`nwb-schema:NWBFile <sec-NWBFile>`.



.. _best_practice_time_series_subtypes:

Subtypes
~~~~~~~~

:ref:`nwb-schema:sec-ElectricalSeries` are reserved for neural data. An
:ref:`nwb-schema:sec-ElectricalSeries` holds signal from electrodes positioned in or around the
brain that are monitoring neural activity, and only those electrodes should be in the ``ElectrodeTable``.

For non-neural electrodes that still may store and report raw values in Volts, simply use a general
:ref:`nwb-schema:sec-TimeSeries` object with ``units`` set to "Volts".



.. _best_practice_timestamps_ascending:

Breaks in Continuity
~~~~~~~~~~~~~~~~~~~~
The ``data`` field of :ref:`nwb-schema:sec-TimeSeries` should generally be stored as one continuous stream
as it was acquired, not by trial as is often reshaped for analysis.

Data can be trial-aligned on-the-fly using the ``TrialTable``.

Storing measured data as a continuous stream ensures that other users have access to the inter-trial data, and that we
can align the data within any specifiable window.

If you only have data spanning specific segments of time, then only include those timepoints in the data, see
:ref:`best_practice_regular_timestamps` for more information.

A primary implication is that the values in :ref:`nwb-schema:TimeSeries.timestamps <sec-TimeSeries>`, as well as the
corresponding ordering of their indices in the :ref:`nwb-schema:TimeSeries.data <sec-TimeSeries>` array, should always
be strictly increasing.

Check function: :py:meth:`~nwbinspector.checks._time_series.check_timestamps_ascending`



.. _best_practice_timestamps_without_nans:

Timestamps without NaNs
~~~~~~~~~~~~~~~~~~~~~~~

The ``timestamps`` field of a :ref:`nwb-schema:sec-TimeSeries` should not contain ``NaN`` values, as this can lead to
ambiguity in time references and potential issues in downstream analyses.

Ensure that all timestamps are valid numerical values. If gaps in time need to be represented, consider segmenting the
data into separate :ref:`nwb-schema:sec-TimeSeries` objects with appropriate ``starting_time`` or use the ``timestamps``
vector to explicitly represent time gaps.

Check function: :py:meth:`~nwbinspector.checks._time_series.check_timestamps_without_nans`




.. _best_practice_regular_timestamps:

Timestamps vs. Start & Rate
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:ref:`nwb-schema:sec-TimeSeries` allows you to specify time using either ``timestamps`` or ``rate``
together with ``starting_time`` (which defaults to 0). If the sampling rate is constant, then specify the ``rate`` and
``starting_time`` instead of writing the full ``timestamps`` vector.

For segmented data, refer to the section covering :ref:`best_practice_timestamps_ascending`;

    1. If the sampling rate is constant within each segment, each segment can be written as a separate
    :ref:`nwb-schema:sec-TimeSeries` with the ``starting_time`` incremented appropriately.

    2. Even if the sampling rate is constant within each segment, a single :ref:`nwb-schema:sec-TimeSeries` can be
    written using the ``timestamps`` vector to appropriately indicate the gaps between segments.

Check function: :py:meth:`~nwbinspector.checks._time_series.check_regular_timestamps`


.. _best_practice_avoid_negative_timestamps:

Avoid Negative Timestamps
~~~~~~~~~~~~~~~~~~~~~~~~~

When writing :ref:`nwb-schema:sec-TimeSeries` data, avoid using negative timestamps.

All timestamps in the NWBFile are written with respect to a global reference point (either ``timestamps_reference_time`` or ``session_start_time``).

While negative timestamps are technically valid, they might introduce unnecessary complications for future users of the file.
In most cases, negative timestamps may be indicative of an alignment error or a problem with the source data.
As much as possible, re-align the session start time so that all timestamps are positive and correctly referenced to either ``timestamps_reference_time`` or ``session_start_time``.
See :ref:`best_practice_global_time_reference` for more details.

Check function: :py:meth:`~nwbinspector.checks._time_series.check_timestamp_of_the_first_sample_is_not_negative`

.. _best_practice_chunk_data:

Chunk Data
~~~~~~~~~~

Use chunking to optimize reading of large data for your use case.

By default, when using the HDF5 backend, :ref:`nwb-schema:sec-TimeSeries` ``data`` are stored on disk using
column-based ordering.

This means that if the ``data`` of a :ref:`nwb-schema:sec-TimeSeries` has multiple dimensions, then all data from a
single timestamp are stored contiguously on disk, followed by the next timestamp, and so on.

This storage scheme may be optimal for certain uses, such as slicing :ref:`nwb-schema:sec-TimeSeries` by time; however,
it may be sub-optimal for other uses, such as reading data from all timestamps for a particular value in the second or
third dimension.

This is especially important when writing NWBFiles that are intended to be uploaded to the
:dandi-archive:`DANDI Archive <>` for storage, sharing, and publication.

For more information about how to enable chunking and compression on your data, consult the
:pynwb-docs:`PyNWB tutorial <tutorials/advanced_io/h5dataio.html#chunking>` or the
`MatNWB instructions <https://matnwb.readthedocs.io/en/latest/pages/tutorials/dataPipe.html>`_.



.. _best_practice_compression:

Compress Data
~~~~~~~~~~~~~

Data writers can optimize the storage of large data arrays for particular uses by using compression applied to each
chunk individually. This is especially important when writing NWBFiles that are intended to be uploaded to the
:dandi-archive:`DANDI Archive <>` for storage, sharing, and publication. For more information about how to enable compression on your data, consult the
:pynwb-docs:`PyNWB tutorial <tutorials/advanced_io/h5dataio.html#compression-and-other-i-o-filters>` or the
`MatNWB instructions <https://matnwb.readthedocs.io/en/latest/pages/tutorials/dataPipe.html>`_

Check functions: :py::meth:`~nwbinspector.checks._nwb_containers.check_large_dataset_compression`,
:py::meth:`~nwbinspector.checks._nwb_containers.check_small_dataset_compression`



.. _best_practice_resolution:

Unknown Resolution
~~~~~~~~~~~~~~~~~~

If the ``resolution`` of a :ref:`nwb-schema:sec-TimeSeries` is unknown, use ``-1.0`` or ``NaN`` to indicate this.

Check function: :py::meth:`~nwbinspector.checks._time_series.check_resolution`



.. _best_practice_non_zero_rate:

Zero Rate
~~~~~~~~~

If the ``data`` field of :ref:`nwb-schema:sec-TimeSeries` has more than one frame, and according to :ref:`best_practice_data_orientation` this axis ought to be time, then the ``rate`` field should not be ``0.0``.

Check function: :py::meth:`~nwbinspector.checks._time_series.check_rate_is_not_zero`
