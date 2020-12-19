# 1678 Server 2019-2021

![pytest](https://github.com/frc1678/server/workflows/pytest/badge.svg)
![lint](https://github.com/frc1678/server/workflows/lint/badge.svg)

Run `src/setup_environment.py` when you clone the repository.

This will install a [virtual python environment](https://docs.python.org/3/glossary.html#term-virtual-environment)
in the main project directory. It will then install the external dependencies into this environment from PyPI using 
`pip`. (This will NOT install any non-python dependencies such as MongoDB, and Android Debug Bridge as the process for that depends on your 
distribution. You will have to do that manually).

There is also a directory called `data/` that needs specific files like `competition.txt` and a directory called `api_keys/` which contains `tba_key.txt` and `cloud_password.txt`.
The `competition.txt` file is created by `src/setup_competition.py` and the two keys need to be added manually.

When testing from the command line, remember to `activate` the virtual environment (`source .venv/bin/activate` on
bash/zsh). Instructions for other shells, along with more in-depth information about Python virtual environments, can be
found [here](https://docs.python.org/3/library/venv.html).

To run the server in production mode on linux or MacOS make sure to run `export SCOUTING_SERVER_ENV=production`, to take the server out of production mode run, `unset SCOUTING_SERVER_ENV`