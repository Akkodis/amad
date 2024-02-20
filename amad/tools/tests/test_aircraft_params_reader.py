import pytest
import os
from amad.tools.aircraft_params_reader import ExcelFileProcess, CSVFileProcess

test_cases = [
    ("xlsx", ExcelFileProcess),
    ("csv", CSVFileProcess),
]


@pytest.mark.parametrize("file_extension, module", test_cases)
def test_read_file(file_extension, module):
    """
    Test the read_file function for different file extensions.

    Parameters
    ----------
    file_extension : str
        The file extension to be tested.
    module : module
        The module containing the read_file function.

    Returns
    -------
    None

    Raises
    ------
    AssertionError
        If any of the assertions fail.
    """
    filename = r"amad/tools/tests/sample_aircraft_params." + file_extension
    df_data = module(filename).read_data()

    # read raw data
    assert df_data.loc[3]["Parameter"] == "h_fuse"
    assert float(df_data.loc[1]["Value"]) == 34.50
    assert df_data.loc[3]["OAD"] == "X"


@pytest.mark.parametrize("file_extension, module", test_cases)
def test_read_parameters(file_extension, module):
    """
    Test the read_parameters function.

    Parameters
    ----------
    file_extension : str
        The file extension used to construct the filename.
    module : object
        The module that contains the read_parameters function.

    Returns
    -------
    None

    Raises
    ------
    AssertionError
        If the first key in the dict_params is not 'h_fuse'.
    """
    filename = r"amad/tools/tests/sample_aircraft_params." + file_extension
    dict_params = module(filename).read_parameters(
        category="OAD", columns=["Parameter", "Unit", "Description", "Value"]
    )
    assert next(iter(dict_params)) == "h_fuse"


@pytest.mark.parametrize("file_extension, module", test_cases)
def test_write_file(file_extension, module):
    """
    Test the write file function for different file extensions.

    Parameters
    ----------
    file_extension : str
        The extension of the file to be tested.
    module : module
        The module containing the file manipulation functions.

    Raises
    ------
    AssertionError
        If the output file does not exist or cannot be removed.
    """
    filename = r"amad/tools/tests/sample_aircraft_params." + file_extension
    df_data = module(filename).read_data()
    df_data = df_data[df_data["Value"].notna()]

    out_filepath = r"amad/tools/tests/out." + file_extension
    module(filename).write_data(df_data, out_filepath)

    file_check = os.path.exists(out_filepath)

    assert file_check is True

    if file_check is True:
        os.remove(out_filepath)
