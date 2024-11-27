ImageSeries
===========

Storage of ImageSeries
----------------------

.. _best_practice_use_external_mode:

Use external mode for videos of animals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When storing videos of natural behavior using the :ref:`nwb-schema:sec-ImageSeries` the file should be stored as
an external file. That is, the file should be packaged together with the nwb file instead of stored inside the format.
This can be accomplished by using  the ``external_file`` file option to store the path instead. This is preferred for
videos because it allows the usage of video compression codecs that are lossy and highly optimized for such videos.

Check function: :py:meth:`~nwbinspector.checks._image_series.check_image_series_data_size`


Use internal dataset for videos of neurophysiological data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When storing a :ref:`nwb-schema:sec-TwoPhotonSeries` or other videos of neural data, lossy compression should not be used,
and it is best to store the this data within a Dataset in the NWB file and use chunking and lossless compression to reduce
the disk space.


.. _best_practice_image_series_external_file_relative:

Use relative path for external mode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When using ``external_file`` the paths passed in the ``external_file`` option should be relative to the location of the nwb file.

Check function: :py:meth:`~nwbinspector.checks._image_series.check_image_series_external_file_relative`
