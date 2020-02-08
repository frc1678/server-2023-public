# 1678 Server 2020

Run `setup_environment.py` when you clone the repository.

This will install a [virtual python environment](https://docs.python.org/3/glossary.html#term-virtual-environment)
in the main project directory. It will then install the external dependencies into this environment from PyPI using 
`pip`. (This will NOT install any non-python dependencies such as MongoDB, as the process for that depends on your 
distribution. You will have to do that manually).

When testing from the command line, remember to `activate` the virtual environment (`source .venv/bin/activate` on
bash/zsh). Instructions for other shells, along with more in-depth information about Python virtual environments, can be
found [here](https://docs.python.org/3/library/venv.html).
