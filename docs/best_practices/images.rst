Images
======

Storage of Images
-----------------

.. _best_practice_order_of_images_unique:
.. _best_practice_order_of_images_len:

Storing the order of images in an Images object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``order_of_images`` field of an :ref:`nwb-schema:sec-Images` object is designed to contain the order
of the images in the ``images`` field of the :ref:`nwb-schema:sec-Images` object. As such, all of the values
in the ``order_of_images`` field should be unique, and its length should be equal to the number of
:ref:`nwb-schema:sec-Image` objects in the :ref:`nwb-schema:sec-Images` object.

Check functions: :py:meth:`~nwbinspector.checks._images.check_order_of_images_unique` and
:py:meth:`~nwbinspector.checks._images.check_order_of_images_len`


.. _best_practice_index_series_points_to_image:

Use of IndexSeries
~~~~~~~~~~~~~~~~~~

The use of an :ref:`nwb-schema:sec-IndexSeries` object to point to a :ref:`nwb-schema:sec-TimeSeries` will
be deprecated in a future release of the NWB schema. The :ref:`nwb-schema:sec-IndexSeries` object should
point to an :ref:`nwb-schema:sec-Images` container, which holds a collection of :ref:`nwb-schema:sec-Image`
objects instead.

Check function: :py:meth:`~nwbinspector.checks._images.check_index_series_points_to_image`
