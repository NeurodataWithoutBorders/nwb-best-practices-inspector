.. image:: logo/logo.png

..
  :scale: 100 %
  :align: right

NWB Inspector
=============
NWB Inspector is a Python-based package designed to asses the quality of Neurodata Without Borders (NWB)
files and based on compliance with Best Practice. This tool is meant as a companion to the PyNWB validator, which checks for strict schema compliance. In contrast, this tool attempts to apply some commonsense rules and heuristics to find data components of a file that pass validation, but are probably incorrect, or suboptimal, or deviate from best practices. In other words, while the PyNWB validator focuses on compliance of the structure of a file with the schema, the inspector focuses on compliance of the actual data with best practices. The NWB Inspector is meant simply as a data review aid. It does not catch all best practice violations, and any warnings it does produce should be checked by a knowledgeable reviewer.

.. toctree::
   :maxdepth: 2

   best_practices/best_practices_index
   user_guide/user_guide_index
   developer_guide
   contributing_checks
   checks_by_importance


.. toctree::
    :maxdepth: 2
    :caption: API Documentation

    Check Functions <api/checks>
    Core Functions <api/nwbinspector>
    Data Classes and Check Registration <api/register_check>
    Organization and Display Tools <api/tools>
    Generic Utils <api/utils>


For more information regarding the NWB Standard, please view the `NWB Format Specification <https://nwb-schema.readthedocs.io/en/latest/>`_.

.. Indices and tables
.. ==================
..
.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`
