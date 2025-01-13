Developer Guide
===============

There are many ways to contribute to the NWBInspector!

Please always begin this process by :nwbinspector-issues:`submitting an Issue ticket <>` on the main repository so we can
openly discuss it taking action. Please do not open a Pull Request (PR) until the Issue has been approved by the team.

The most common contribution is to help us add new Best Practices and check functions for them. We have a detailed guide on
:doc:`how to contribute new checks <contributing_checks>`.

Otherwise feel free to raise a bug report, documentation mistake, or general feature request for our maintainers to address!


Coding Style and pre-commit
---------------------------

We use the :black-coding-style:`black coding style <>` with parameters defined in the ``pyproject.toml`` configuration file. We use an automated pre-commit bot to enforce these on the main repo, but contributions from external forks would either have to grant bot permissions on their own fork (via :pre-commit-bot:`the pre-commit bot website <>`) or run pre-commit manually. For instructions to install pre-commit, as well as some other minor coding styles we follow, refer to the :neuroconv-coding-style:`NeuroConv style guide <>`.



.. _adding_custom_checks:

Adding Custom Checks to the Registry
------------------------------------

If you are writing an extension, or have any personal Best Practices specific to your lab, you can incorporate these
into your own usage of the NWBInspector. To add a custom check to your default registry, all you have to do is wrap
your check function with the :py:class:`~nwbinspector.register_checks.register_check` decorator like so...

.. code-block:: python

    from nwbinspector.register_checks import available_checks, register_check, Importance

    @register_check(importance=Importance.SOME_IMPORTANCE_LEVEL, neurodata_type=some_neurodata_type)
    def check_personal_practice(...):
        ...

Then, all that is needed for this to be automatically included when you run the inspector through the CLI is to specify
the modules flag ``-m`` or ``--modules`` along with the name of your module that contains the custom check. If using
the library instead, you need only import the ``available_checks`` global variable from your own submodules, or
otherwise import your check functions after importing the ``nwbinspector`` in your ``__init__.py``.


Disable Tests That Require Network Connection
---------------------------------------------

Some of the tests in the suite require internet connectivity both to and from the DANDI archive S3 bucket.
If this is failing for some reason, you can explicitly control all related tests by setting the environment variable
``NWBI_SKIP_NETWORK_TESTS`` to some value able to be parsed by ``nwbinspector.utils.strtobool``. For example, to disable them on
a linux system, run

.. code-block::

    export NWBI_SKIP_NETWORK_TESTS=1

in your environment before running ``pytest``.


Making a Release
----------------

To prepare a release, follow these steps and make a new pull request with the changes:

    1. Update the ``CHANGELOG.md`` header with the upcoming version number and ensure all upcoming changes are included.
    2. Update the version string in ``pyproject.toml``.
    3. Check the requirements versions and update if needed.
    4. Update dates in ``docs/conf.py`` and ``license.txt`` to the current year if needed.

After merging, follow these steps:

    1. Create a new git tag. Pull the latest dev branch, then run the following commands (updating the release version)
       to create the tag and push to GitHub.

    .. code-block::

        release=X.Y.Z
        git tag ${release} --sign -m "nwbinspector ${release}"
        git push --tags

    2. On the `GitHub tags <https://github.com/NeurodataWithoutBorders/nwbinspector/tags>`_ page, click "..." -> "Create release" on the new tag.
       Fill in the release notes from the ``CHANGELOG.md`` and publish the release.
    3. Publishing a release on GitHub will trigger the ``auto-publish.yml`` action on the CI that will publish the package on PyPi.
    4. Conda-forge maintains a bot that regularly monitors PyPi for new releases of packages that are also on conda-forge.
       When a new release is detected, the bot will create a pull request. Follow the instructions in that pull request to update any requirements.
       Once the PR is approved and merged, a new release will be published on conda-forge.
