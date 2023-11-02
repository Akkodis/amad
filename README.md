# AMAD - AKKODIS MDAO Aircraft Demonstrator ✈︎
`AMAD` is a multi disciplinary design analysis and optimization (MDAO) tool kit for aircraft optimization.
The initial version covers a conventional aircraft example.
The optimization and multi dsisciplinary approach is based on the [CoSApp](https://gitlab.com/cosapp/cosapp) environment.
## Implemented Disciplines
- Aircraft Geometry
- Aerodynamics
- Aircraft Mass estimation (Raymer, Torenbeek)
- Turbofan Engine (Mattingly)
- Mission Performance
- Support Routines (ISA Atmosphere, Unit Conversions, etc.)

## External optional dependencies
- AVL for aero computation: https://web.mit.edu/drela/Public/web/avl/
- XFOIL for airfoil computation: https://web.mit.edu/drela/Public/web/xfoil/

## Included Python Packages
- AeroSandbox: https://github.com/peterdsharpe/AeroSandbox
- CoSApp: https://cosapp.readthedocs.io/en/latest/

## Example demo notebooks
Example and demo jupyter notebooks for different subjects are available in the `amad/demo/notebooks` folder.

## Installation example
#### Create environment using Conda:
`conda create -n amad pip git`
<br>`conda activate amad`
<br> CLone/Download AMAD repository: 
<br>`git clone https://github.com/Akkodis/amad.git`

#### Install libraries and dependencies:
in folder containing `pyproject.toml` file: 
<br>`python -m pip install .`
<br>launch: `jupyter lab`

## Contributors
Peter CAIRNS
<br> Rafael Rojas CARDENAS
<br> André HOCHSCHULZ

## Contact
amad@akkodis.com





 
sphinx- 