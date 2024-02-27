# Installation example
## Create environment using Conda
```console
conda create -n amad pip git pandoc
conda activate amad
```

## Clone/Download AMAD repository
```console
git clone https://github.com/Akkodis/amad.git
```

## Install libraries and dependencies
in folder containing `pyproject.toml` file:
```console
python -m pip install .
jupyter lab
```
<br> There are also `dev` and `doc` environments included.

