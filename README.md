<p align="center">
  <img src="https://raw.githubusercontent.com/neurodatawithoutborders/nwbinspector/dev/docs/logo/logo.png" width="250" alt="NWB Inspector logo"/>

  <p align="center">
    <a href="https://pypi.org/project/dandi_s3_log_parser/"><img alt="Supported Python versions" src="https://img.shields.io/pypi/pyversions/nwbinspector.svg"></a>
    <a href="https://codecov.io/github/CatalystNeuro/dandi_s3_log_parser?branch=main"><img alt="codecov" src="https://codecov.io/github/NeurodataWithoutBorders/nwbinspector/coverage.svg?branch=main"></a>
  </p>
  <p align="center">
    <a href="https://pypi.org/project/nwbinpsector/"><img alt="PyPI latest release version" src="https://badge.fury.io/py/nwbinspector.svg?id=py&kill_cache=1"></a>
    <a href="https://github.com/NeurodataWithoutBorders/nwbinspector/blob/dev/license.txt"><img alt="License: BSD-3" src="https://img.shields.io/pypi/l/nwbinspector.svg"></a>
  </p>
  <p align="center">
    <a href="https://github.com/psf/black"><img alt="Python code style: Black" src="https://img.shields.io/badge/python_code_style-black-000000.svg"></a>
    <a href="https://github.com/astral-sh/ruff"><img alt="Python code style: Ruff" src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json"></a>
  </p>
  <p align="center">
    <a href="https://nwbinspector.readthedocs.io/"><img alt="Documentation build status" src="https://readthedocs.org/projects/nwbinspector/badge/?version=dev"></a>
    <a href="https://github.com/NeurodataWithoutBorders/nwbinspector/actions/workflows/dailies.yml/badge.svg"><img alt="Daily tests" src="https://github.com/NeurodataWithoutBorders/nwbinspector/actions/workflows/dailies.yml/badge.svg"></a>
  </p>
</p>

Inspect NWB files for compliance with [NWB Best Practices](https://nwbinspector.readthedocs.io/en/dev/best_practices/best_practices_index.html).

This inspector is meant as a companion to the PyNWB validator, which checks for strict schema compliance. This tool attempts to apply some common sense to find components of the file that are technically compliant, but possibly incorrect, suboptimal in their representation, or deviate from best practices.

This tool is meant simply as a data review aid. It does not catch all possible violations of best practices and any warnings it does produce should be checked by a knowledgeable reviewer.



## Installation

```bash
pip install nwbinspector
```



## Usage

```bash
# supply a path to an NWB file
nwbinspector path/to/my/data.nwb

# supply a path to a directory containing NWB files
nwbinspector path/to/my/data/folder/
```

Read about more detailed usage in the main [documentation](https://nwbinspector.readthedocs.io/en/dev/user_guide/user_guide_index.html).
