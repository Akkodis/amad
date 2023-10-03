def whichTool(program):
    """ Test Routine to check if external executable tool is available based on path variable.

    Args:
        program (str): external tool name (e.g. 'AVL.exe')

    Returns:
        bool: existing or not
    """

    import os

    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ.get("PATH", "").split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None
