Extracellular electrophysiology
===============================



Electrodes
----------


.. _best_practice_ecephys_location:

Location
~~~~~~~~

The ``location`` column of the ``ElectrodeTable`` should reflect your best estimate of the recorded
brain area. Different labs have different standards for electrode localization. Some use atlases and coordinate maps to
precisely place an electrode, and use physiological measures to confirm its placement. Others use histology or imaging
processing algorithms to identify regions after-the-fact. You fill this column with localization results from your most
accurate method. For instance, if you target electrodes using physiology, and later use histology to confirm placement,
we would recommend that you add a new column to the electrodes table called 'location_target', set those values to the
original intended target, and alter the values of 'location' to match the histology results.

The ``location`` column of the ``ElectrodeTable`` is required. If you do not know the location of
an electrode, use "unknown".



.. _best_practice_ecephys_ontologies:

Ontologies
~~~~~~~~~~

It is preferable to use established ontologies instead of lab conventions for indicating anatomical region.
We recommend the :allen-brain-map:`Allen Brain Atlas <atlas>` terms for mice, and you may use either the full name or
the abbreviation (do not make up your own terms).



.. _best_practice_ecephys_anatomical_coordinates:

Anatomical Coordinates
~~~~~~~~~~~~~~~~~~~~~~

The ``x``, ``y``, and ``z`` columns of the ``ElectrodeTable`` are for the precise anatomical
coordinates within the Subject. For mice, use the
:allen-brain-map:`Allen Institute Common Coordinate Framework v3 <atlas>`, which follows the convention
(+x = posterior, +y = inferior, +z = subject's right).



.. _best_practice_ecephys_relative_coordinates:

Relative Coordinates
~~~~~~~~~~~~~~~~~~~~

For relative position of an electrode on a probe, use ``rel_x``, ``rel_y``, and ``rel_z`` columns of the
``ElectrodeTable``. These positions will be used by spike sorting software to determine electrodes
that are close enough to share a neuron.


Avoid Duplication of Metadata
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``ElectrodeTable`` should not contain redundant information that is present somewhere else within the :ref:`nwb-schema:sec-NWBFile` . Avoid adding columns to the `ElectrodeTable` that correspond to properties of the :ref:`nwb-schema:sec-ElectricalSeries` such as ``unit``, ``offsets`` or ``channel gains`` These properties should be stored in the corresponding attributes of the :ref:`nwb-schema:sec-ElectricalSeries` object.

As a concrete example, the package objects from the `SpikeInterface <https://spikeinterface.readthedocs.io/en/latest/>`__ package contain two properties named ``gain_to_uv`` and ``offset_to_uv`` that are used to convert the raw data to microvolts. These properties should not be stored in the `ElectrodeTable` but rather in the ``ElectricalSeries`` object as ``channel_conversion`` and ``offset`` respectively.

Units Table
-----------

.. _best_practice_negative_spike_times:

Negative Spike Times
~~~~~~~~~~~~~~~~~~~~

All spike times should be greater than zero. Being less than zero implies the spikes are either trial-aligned (and
should therefore be aligned to the ``timestamps_reference_time`` of the :ref:`nwb-schema:sec-NWBFile`) or the
``timestamps_reference_time`` itself is not set to the earliest recording time during the session.

Check function: :py:meth:`~nwbinspector.checks._ecephys.check_negative_spike_times`



.. _best_practice_spike_times_not_in_unobserved_interval:

Observation Intervals
~~~~~~~~~~~~~~~~~~~~~

The ``obs_intervals`` field of the :ref:`nwb-schema:sec-units-src` table is used to indicate periods of time where the underlying electrical signal(s) were not observed. This can happen if the recording site moves away from the unit, or if the recording is stopped. Since the channel is not observed, it is not determinable whether a spike occurred during this time. Therefore, there should not be any identified spike times for units matched to those electrical signal(s) occurring outside of the defined ``obs_intervals``. If this variable is not set, it is assumed that all time is observed.

Check function: :py:meth:`~nwbinspector.checks._ecephys.check_spike_times_not_in_unobserved_interval`
