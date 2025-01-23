Contributing New Checks
=======================

This guide will walk you through the process of contributing a new check to NWBInspector.

Overview
--------

NWBInspector checks are Python functions that examine NWB files for compliance with best practices. Each check is:

1. Focused on a specific aspect of NWB files
2. Decorated with :py:func:`~nwbinspector._registration.register_check`
3. Returns either ``None`` (pass) or :py:class:`~nwbinspector._types.InspectorMessage` (fail)

Step-by-Step Guide
------------------

1. Propose Your Check
^^^^^^^^^^^^^^^^^^^^^

Before writing code:

1. Open a :nwbinspector-issues:`'New Check' issue <>`
2. Describe what the check will validate
3. Link to relevant :doc:`best practices documentation <best_practices/best_practices_index>` if applicable. If proposing a new best practice, please describe in detail.
4. Wait for approval before proceeding

2. Choose the Right Location
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Checks are organized by category in ``src/nwbinspector/checks/``. Choose the appropriate file based on what you're checking:

1. ``_nwbfile_metadata.py`` - General :py:class:`~pynwb.file.NWBFile` metadata
2. ``_nwb_containers.py`` - NWB container objects
3. ``_time_series.py`` - :py:class:`~pynwb.base.TimeSeries` objects
4. ``_tables.py`` - :py:class:`~hdmf.common.table.DynamicTable` objects
5. ``_behavior.py`` - Behavioral data
6. ``_icephys.py`` - Intracellular electrophysiology
7. ``_ecephys.py`` - Extracellular electrophysiology
8. ``_ophys.py`` - Optical physiology
9. ``_ogen.py`` - Optogenetics
10. ``_image_series.py`` - :py:class:`~pynwb.image.ImageSeries` objects
11. ``_images.py`` - :py:class:`~pynwb.base.Images` objects
12. ``_general.py`` - attributes of general neurodata types

3. Write Your Check
^^^^^^^^^^^^^^^^^^^

Here's a template for a new check:

.. code-block:: python

    @register_check(
        importance=Importance.BEST_PRACTICE_SUGGESTION,  # Choose appropriate level
        neurodata_type=NWBFile  # Most general applicable type
    )
    def check_my_feature(nwbfile: NWBFile) -> Optional[InspectorMessage]:
        """One-line description of what this check validates."""
        if problem_detected:
            return InspectorMessage(
                message="Clear description of the issue and how to fix it."
            )
        return None
.. note::
   The function name for the check should always start with ``check_``

4. Choose the Right Importance Level
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Select from three levels (see :doc:`checks_by_importance` for examples):

1. ``Importance.CRITICAL``: High likelihood of incorrect data that can't be caught by PyNWB validation
2. ``Importance.BEST_PRACTICE_VIOLATION``: Major violation of :doc:`Best Practices <best_practices/best_practices_index>`
3. ``Importance.BEST_PRACTICE_SUGGESTION``: Minor violation or missing optional metadata

5. Write Tests
^^^^^^^^^^^^^^

Add tests in the corresponding test file under ``tests/unit_tests/``. Include both passing and failing cases:

.. code-block:: python

    def test_my_feature_pass():
        # Test case where check should pass
        assert check_my_feature(nwbfile=NWBFile(...)) is None

    def test_my_feature_fail():
        # Test case where check should fail
        assert check_my_feature(nwbfile=make_minimal_nwbfile()) == InspectorMessage(
            message="Expected message"
        )

6. Add Check to the Public Interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
1. Add an import for your check from the appropriate module in ``src/nwbinspector/checks/__init__.py``
2. Add your check to the ```__all__``` list in ``src/nwbinspector/checks/__init__.py`` to indicate
   the check is part of the public interface.


7. Add Check to the Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Add a link to your new check function in the relevant best practice section of the ``docs/best_practices`` folder.
If needed, add a new section and label for your check:

.. code-block:: rst

    .. _best_practice_my_feature:

    My Feature
    ~~~~~~~~~~

    Description of the best practice.

    Check function: :py:meth:`~nwbinspector.checks._tables.check_my_feature`

.. note::
    If the best practice label in the ``.rst`` file ends with the same pattern as the check function name,
    (e.g. ``.. _best_practice_my_feature:``  and ``check_my_feature``), a link to the best practice documentation
    will be automatically added to the function API documentation.

    However, if the name of your check function does not match the name of your best practice section label
    (e.g. if a single best practices section has multiple check functions), you can include a link in the function
    docstring to link to the related best practice section.

    .. code-block:: python

        def check_my_feature(nwbfile: NWBFile) -> Optional[InspectorMessage]:
            """
            One-line description of what this check validates.

            Best Practice: :ref:`best_practice_my_feature_unique_label`
            """

7. Best Practices for Check Implementation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Keep logic simple and focused
2. Use descriptive variable names
3. Add comments for complex logic
4. Reuse utility functions from :doc:`api/utils` when possible
5. Make error messages clear and actionable
6. Include links to relevant documentation in docstrings

8. Submit Your PR
^^^^^^^^^^^^^^^^^

1. Create a new branch
2. Add your check and tests
3. Run the test suite
4. Submit a Pull Request
5. Respond to review feedback

Example Check
-------------

Here's a complete example of a well-implemented check:

.. code-block:: python

    @register_check(
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        neurodata_type=NWBFile
    )
    def check_experimenter(nwbfile: NWBFile) -> Optional[InspectorMessage]:
        """Check if an experimenter has been added for the session."""
        if not nwbfile.experimenter:
            return InspectorMessage(
                message="Experimenter is missing. Add experimenter information to improve metadata completeness."
            )
        return None

For more examples, see the :doc:`api/checks` documentation.

Common Pitfalls
---------------

1. **Too Broad**: Checks should validate one specific thing
2. **Unclear Messages**: Error messages should clearly explain the issue and how to fix it
3. **Missing Tests**: Always include both passing and failing test cases
4. **Wrong Importance**: Carefully consider the impact of the issue being checked
5. **Redundant Checks**: Ensure your check isn't duplicating existing functionality

Need Help?
----------

1. Review existing :doc:`api/checks` for examples
2. Ask questions in your :nwbinspector-issues:`issue <>` before starting implementation
3. Request review from maintainers early in the process
