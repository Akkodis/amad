import abc
import pandas as pd


class AbstractFileProcessor:
    """
    ParamsFileProcess object is a class for Parameters Excel File Processing.
    """

    def __init__(self, file_name_path=""):
        """
        Initialisation of AbstractFileProcessor.

        Parameters
        ----------
        file_name_path : str
            Excel file name with path.

        Returns
        -------
        None
        """

        self.file_name_path = file_name_path
        self.df_data = pd.DataFrame()

    @abc.abstractmethod
    def read_data(self):
        """
        Read File into Pandas DataFrame

        Parameters:
            None

        Returns:
            df_data (DataFrame):
        """
        pass

    def read_parameters(self, category: str, columns: list):
        """
        Read Parameters for a specific discipline from a file

        Parameters
        ----------
        category : str
            Name of the column to filter by

        columns : list
            List of columns to extract

        Returns
        -------
        dict
            The parameters in a dictionary
        """

        # read in data, keeping only a specific category of parameters
        df = self.read_data()
        df = df[df[category] == "X"].reset_index(drop=True)

        # keep useful columns and set index to Parameter
        df = df[columns].set_index("Parameter")

        # convert to dictionary
        parameters_dict = df.to_dict("index")

        return parameters_dict

    @abc.abstractmethod
    def write_data(self, df_data: object, file_name_path: str):
        """
        Write df_data DataFrame into output file

        Parameters
        ----------
        file_name_path : str
            Excel file name with path.
        df_data : DataFrame
            Excel sheet data.

        Returns
        -------
        None
        """
        pass


class ExcelFileProcess(AbstractFileProcessor):
    """
    Excel File Processing
    """

    def read_data(self):
        """
        Read data from an Excel file.

        Returns
        -------
        pandas DataFrame
            The data read from the Excel file.

        Raises
        ------
        FileNotFoundError
            If the file specified by `file_name_path` does not exist.
        """
        self.df_data = pd.read_excel(self.file_name_path, keep_default_na=False)
        return self.df_data

    def write_data(self, df_data: object, file_name_path: str):
        """
        Write DataFrame data to an Excel file.

        Parameters
        ----------
        df_data : object
            A Pandas DataFrame object containing the data.

        file_name_path : str
            The path and file name of the output Excel file.

        Returns
        -------
        None

        Note
        ----
        The function will save the DataFrame data to the specified Excel file.
        """
        df_data.to_excel(file_name_path)
        return


class CSVFileProcess(AbstractFileProcessor):
    """
    CSV File Processing
    """

    def read_data(self):
        """
        Read data from a CSV file and return as a pandas DataFrame.

        Returns
        -------
        pandas.DataFrame
            The DataFrame containing the data from the CSV file.

        Raises
        ------
        FileNotFoundError
            If the specified file cannot be found.
        """
        self.df_data = pd.read_csv(self.file_name_path, keep_default_na=False)
        return self.df_data

    def write_data(self, df_data: object, file_name_path: str):
        """
        Write DataFrame to a CSV file.

        Parameters
        ----------
        df_data : pandas DataFrame object
            The DataFrame containing the data to be written to a CSV file.
        file_name_path : str
            The file path and name where the CSV file will be saved.

        Returns
        -------
        None
        """
        df_data.to_csv(file_name_path)
        return
