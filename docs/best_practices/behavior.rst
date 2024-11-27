Behavior
========


SpatialSeries
-------------

:ref:`nwb-schema:sec-SpatialSeries` objects are specifically for the position (angular or translational) of a Subject over time. Related data such as velocity and acceleration should be placed in a different neurodata object.

.. _best_practice_spatial_series_dimensionality:

SpatialSeries Dimensionality
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:ref:`nwb-schema:sec-SpatialSeries` should have 1 column (x), 2 columns (x, y), or 3 columns (x, y, z).

Check function: :py:meth:`~nwbinspector.checks._behavior.check_spatial_series_dims`


.. _best_practice_spatial_series_units:

SpatialSeries Units
~~~~~~~~~~~~~~~~~~~

When a :ref:`nwb-schema:sec-SpatialSeries` is in a :ref:`nwb-schema:sec-CompassDirection`, the units should either be
"degrees" or "radians".

Check function: :py:meth:`~nwbinspector.checks._behavior.check_compass_direction_unit`


.. _best_practice_spatial_series_values:

SpatialSeries Data Values
~~~~~~~~~~~~~~~~~~~~~~~~~

When a :ref:`nwb-schema:sec-SpatialSeries` has units "radians", it should have data values between -2π and 2π. When a
:ref:`nwb-schema:sec-SpatialSeries` has units "degrees", it should have data values between -360 and 360.

Check functions: :py:meth:`~nwbinspector.checks.behavior.check_spatial_series_radians_magnitude`,
:py:meth:`~nwbinspector.checks._behavior.check_spatial_series_degrees_magnitude`
