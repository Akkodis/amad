# Import the first class found in each file having the same name
# as the file (test is case insensitive).
#
# Copyright (C) 2018-2021, CoSApp Team - Safran Group
#
# DO NOT MODIFY this file. It is automatically handled by CoSApp.
import logging

logger = logging.getLogger(__name__)


def _import_all_modules():
    """Dynamically imports all systems in the package."""
    import inspect
    import os

    all_objects = []
    globals_, locals_ = globals(), locals()

    # dynamically import all the package modules
    modules = set()
    for filename in os.listdir(os.path.dirname(__file__)):
        # process all python files in directory that don't start with underscore
        # (which also keeps this module from importing itself)
        modulename, ext = os.path.splitext(filename)
        if filename[0] != "_" and ext == ".py":
            modules.add(modulename)

    old_length = len(modules) + 1
    errors = {}
    while len(modules) and old_length > len(modules):
        old_length = len(modules)
        for modulename in modules.copy():
            package_module = ".".join([__name__, modulename])
            try:
                module = __import__(package_module, globals_, locals_, [modulename])
            except ModuleNotFoundError as err:
                raise err
            except ImportError as err:
                errors[modulename] = repr(err)
                continue

            # Only the class with the same name as the file will be imported
            found_class = False
            for obj_name in filter(lambda name: name[0] != "_", module.__dict__):
                found_class = modulename.lower() == obj_name.lower()
                obj = module.__dict__[obj_name]
                if found_class and inspect.isclass(
                    obj
                ):  # Check that the object found is a class
                    globals_[obj_name] = module.__dict__[obj_name]
                    all_objects.append(obj_name)
                    break

            if not found_class:
                logger.warning(
                    "File {}.py does not contain a class named {}. The file will be ignored."
                    "".format(package_module, modulename)
                )

            modules.discard(modulename)  # Remove module from the available list

    if modules:
        logger.warning("Failed to import from {} modules {}.".format(__name__, modules))
        for modulename in modules:
            logger.debug("{}: {}".format(modulename, errors[modulename]))

    return all_objects


__all__ = _import_all_modules()
