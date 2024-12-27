Contributing New Checks
=======================

This guide will walk you through the process of contributing a new check to NWBInspector.

Overview
--------

NWBInspector checks are Python functions that examine NWB files for compliance with best practices. Each check is:

1. Focused on a specific aspect of NWB files
2. Decorated with ``@register_check``
3. Returns either ``None`` (pass) or an ``InspectorMessage`` (fail)

Step-by-Step Guide
------------------

1. Propose Your Check
^^^^^^^^^^^^^^^^^^^^^

Before writing code:

1. Open a `'New Check' issue <https://github.com/NeurodataWithoutBorders/nwbinspector/issues/new/choose>`_
2. Describe what the check will validate
3. Link to relevant best practices documentation
4. Wait for approval before proceeding

2. Choose the Right Location
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Checks are organized by category in ``src/nwbinspector/checks/``. Choose the appropriate file based on what you're checking:

- ``_nwbfile_metadata.py`` - General NWBFile metadata
- ``_nwb_containers.py`` - NWB container objects
- ``_time_series.py`` - TimeSeries objects
- ``_tables.py`` - Table objects
- ``_behavior.py`` - Behavioral data
- ``_icephys.py`` - Intracellular electrophysiology
- ``_ecephys.py`` - Extracellular electrophysiology
- ``_ophys.py`` - Optical physiology
- ``_ogen.py`` - Optogenetics
- ``_image_series.py`` - ImageSeries objects

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

4. Choose the Right Importance Level
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Select from three levels:

- ``Importance.CRITICAL``: High likelihood of incorrect data that can't be caught by PyNWB validation
- ``Importance.BEST_PRACTICE_VIOLATION``: Major violation of `Best Practices <https://www.nwb.org/best-practices/>`_
- ``Importance.BEST_PRACTICE_SUGGESTION``: Minor violation or missing optional metadata

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

6. Best Practices for Check Implementation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Keep logic simple and focused
2. Use descriptive variable names
3. Add comments for complex logic
4. Reuse utility functions from ``utils.py`` when possible
5. Make error messages clear and actionable
6. Include links to relevant documentation in docstrings

7. Submit Your PR
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

Common Pitfalls
---------------

1. **Too Broad**: Checks should validate one specific thing
2. **Unclear Messages**: Error messages should clearly explain the issue and how to fix it
3. **Missing Tests**: Always include both passing and failing test cases
4. **Wrong Importance**: Carefully consider the impact of the issue being checked
5. **Redundant Checks**: Ensure your check isn't duplicating existing functionality

Need Help?
----------

- Review existing checks for examples
- Ask questions in your issue before starting implementation
- Request review from maintainers early in the process
