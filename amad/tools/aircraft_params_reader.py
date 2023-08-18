import abc
import pandas as pd


class AbstractFileProcessor:
    """
    ParamsFileProcess object is class for Parameters Excel File Processing.
    """

    def __init__(self, file_name_path=""):
        """
        Initialisation of AbstractFileProcessor.
        Args:
            - file_name_path (str): excel file name with path

        Returns:
            - None
        """

        self.file_name_path = file_name_path
        self.df_data = pd.DataFrame()

    @abc.abstractmethod
    def read_data(self):
        """
        Read File into Pandas DataFrame

        Args:
            - None

        Returns:
            - df_data (DataFrame):
        """
        pass

    def read_parameters(self, category: str, columns: list):
        """
        Read Parameters for a specific discipline from a file
        Returns the parameters in a dictionary

        Args:
            category (str): Name of the column to filter by
            columns (list): List of columns to extract
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

        Args:
            - file_name_path (str): excel file name with path
            - df_data (DataFrame): Excel sheet data

        Returns:
            - None
        """
        pass


class ExcelFileProcess(AbstractFileProcessor):
    """
    Excel File Processing
    """

    def read_data(self):
        self.df_data = pd.read_excel(self.file_name_path, keep_default_na=False)
        return self.df_data

    def write_data(self, df_data: object, file_name_path: str):
        df_data.to_excel(file_name_path)
        return


class CSVFileProcess(AbstractFileProcessor):
    """
    CSV File Processing
    """

    def read_data(self):
        self.df_data = pd.read_csv(self.file_name_path, keep_default_na=False)
        return self.df_data

    def write_data(self, df_data: object, file_name_path: str):
        df_data.to_csv(file_name_path)
        return
