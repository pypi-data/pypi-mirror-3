"""
Very simple configuration manager for simple persistent configurations.
"""

import json

import py
import appdirs

AUTHOR_DEFAULT = ''

class ProjectAlreadyExists(Exception):
    """ Raised when trying to create already existing project """


def create_project_config(*args, **kwrds):
    """
    Creates a project configuration file.
    given project name, author and version.
    returns nothing.
    """
    path = _get_project_config_path(*args, **kwrds)
    if path.check():
        raise ProjectAlreadyExists(*args, **kwrds)
    path.ensure()
    set_project_config(*args, **kwrds)({})


def get_project_config(*args, **kwrds):
    """
    Get a project configuration
    given projet name, author and version.
    """
    return json.load(_get_project_config_path(*args, **kwrds))

def project_exists(*args, **kwrds):
    """
    Given project name author and version,
    returns if the project exists
    """
    return _get_project_config_path(*args, **kwrds).check()


def set_project_config(*args, **kwrds):
    """
    Given project name, author and version.
    returns a setter function which gets a dictionary
    to write to the config file.
    """
    def set_config(dictionary):
        """
        Given dictionary,
        updates the configuration of the bounded project.
        """
        _get_project_config_path(*args, **kwrds).write(json.dumps(dictionary))
    return set_config

def delete_project_config(*args, **kwrds):
    """
    Given project name, author and version.
    removes the project configuratio files.
    use carefully.
    """
    _get_project_config_dirpath(*args, **kwrds).remove()


def _get_project_config_path(*args, **kwrds):
    """
    Given project name, author and version
    returns path object of the json config file.
    """
    return _get_project_config_dirpath(*args, **kwrds).join('config.json')

def _get_project_config_dirpath(projectname, author=None, version=None):
    """
    Given project name, author and version
    returns the path object of the configuratin directory.
    """
    author = author or AUTHOR_DEFAULT
    configdir = appdirs.AppDirs(projectname, author, version)
    return py.path.local(configdir.user_data_dir)
