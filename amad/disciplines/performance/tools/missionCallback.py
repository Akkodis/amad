def empty_callback(*kwargs):
    """
    Does nothing. This is an empty callback function.

    Parameters
    ----------
    *kwargs : arguments
        Any number of keyword arguments.

    Returns
    -------
    None
        There is no return value.
    """
    pass


class MissionCallback:
    """
    A class representing a mission callback.

    Methods
    -------
    callback(callback_data)
        A method that triggers the callback function.

    Attributes
    ----------
    callback_method : function
        The function to be called when the callback is triggered.
    """
    def __init__(self):
        """
        Initialize the object.

        Attributes
        ----------
        callback_method : function
            The callback method of the object.
        """
        self.callback_method = empty_callback

    def callback(self, callback_data):
        """
        Call the callback method with the given callback data.

        Parameters
        ----------
        self : object
            The object instance that contains the callback method.
        callback_data : any
            The data to be passed to the callback method.

        Returns
        -------
        None

        Raises
        ------
        None
        """
        self.callback_method(callback_data)


if __name__ == "__main__":

    def print_callback(callback_data):
        """
        Prints the provided callback data.

        Parameters
        ----------
        callback_data : any
            Data to be printed.

        Returns
        -------
        None
            This function does not return a value.
        """
        print(callback_data)

    mc = MissionCallback()
    mc.callback(callback_data="hello world")

    mc.callback_method = print_callback
    mc.callback(callback_data="hello world")
