import pytest
import os
from amad.tools.aircraft_params_reader import ExcelFileProcess, CSVFileProcess

test_cases = [
    ("xlsx", ExcelFileProcess),
    ("csv", CSVFileProcess),
]


@pytest.mark.parametrize("file_extension, module", test_cases)
def test_read_file(file_extension, module):
    filename = r"amad/tools/tests/sample_aircraft_params." + file_extension
    df_data = module(filename).read_data()

    # read raw data
    assert df_data.loc[3]["Parameter"] == "h_fuse"
    assert float(df_data.loc[1]["Value"]) == 34.50
    assert df_data.loc[3]["OAD"] == "X"


@pytest.mark.parametrize("file_extension, module", test_cases)
def test_read_parameters(file_extension, module):
    filename = r"amad/tools/tests/sample_aircraft_params." + file_extension
    dict_params = module(filename).read_parameters(
        category="OAD", columns=["Parameter", "Unit", "Description", "Value"]
    )
    assert next(iter(dict_params)) == "h_fuse"


@pytest.mark.parametrize("file_extension, module", test_cases)
def test_write_file(file_extension, module):
    filename = r"amad/tools/tests/sample_aircraft_params." + file_extension
    df_data = module(filename).read_data()
    df_data = df_data[df_data["Value"].notna()]

    out_filepath = r"amad/tools/tests/out." + file_extension
    module(filename).write_data(df_data, out_filepath)

    file_check = os.path.exists(out_filepath)

    assert file_check is True

    if file_check is True:
        os.remove(out_filepath)
