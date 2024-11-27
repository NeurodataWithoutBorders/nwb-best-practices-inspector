Optogenetics
============

.. _best_practice_optogenetic_stimulus_site_has_optogenetic_series:

OptogeneticSeries
-----------------

Each :ref:`nwb-schema:sec-OptogeneticStimulusSite` object should be referenced by at least one
:ref:`nwb-schema:sec-OptogeneticSeries` in the same file.

Check function: :py:meth:`~nwbinspector.checks._ogen.check_optogenetic_stimulus_site_has_optogenetic_series`
