import pytest
from amad.tools.extToolsCheck import whichTool

test_cases_tools = ['AVL.exe', 'XFOIL.exe']


@pytest.mark.parametrize('prog', test_cases_tools)
# prog = 'AVL.exe'
def test_extTools(prog):
    res = whichTool(prog)
    assert res is not None
