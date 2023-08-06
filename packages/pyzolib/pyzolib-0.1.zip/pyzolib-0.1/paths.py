# -*- coding: utf-8 -*-
# Copyright (c) 2012, The Pyzo team
#
# This file is distributed under the terms of the (new) BSD License.

""" Module paths

Get paths to useful directories in a cross platform manner.

"""

# Notes:
# site.getusersitepackages() returns a dir in roaming userspace on Windows
# so better avoid that.
# site.getuserbase() returns appdata_dir('Python', True)

import os
import sys
import struct

ISWIN = sys.platform.startswith('win')
ISMAC = sys.platform == 'darwin'
ISLINUX = sys.platform.startswith('linux')


def is_frozen():
    """ is_frozen()
    
    Return whether this app is a frozen application
    (using cx_freeze, bbfreeze, py2exe).
    
    """
    return bool( getattr(sys, 'frozen', None) )


def _path_from_environ(*args):
    """ To querry Windows paths in an easy way. """
    for arg in args:
        try:
            value = os.environ[arg]
            if os.path.isdir(value):
                return value
        except KeyError:
            pass
    else:
        return None


def _test_if_dir_exists(path, what):
    if not os.path.isdir(path):
        raise RuntimeError('Detected %s directory "%s" does not exist.' % 
                (what, path))
    return path


def temp_dir(appname=None, nospaces=False, preserved=False):
    """ temp_dir(appname=None)
    
    Get path to a temporary directory with write access. 
    
    If appname is given, a subdir is appended (and created if necessary). 
    
    If nospaces, will ensure that the path has no spaces. If preserved, will
    prefer a directory that preserves the files between sessions (Linux).
    
    """
    #http://www.tuxfiles.org/linuxhelp/linuxdir.html
    #http://en.wikipedia.org/wiki/Filesystem_Hierarchy_Standard
    
    if ISWIN:
        # Default
        path = _path_from_environ('TEMP', 'TMP')
        # Make path invalid if we needed a space-less path and it is not
        if nospaces and ' ' in path:
            path = None
        # On failure, check other common temp dirs
        if not (path and os.path.isdir(path)):
            for path in ['c:\\tmp', 'c:\\temp']:
                if os.path.isdir(path):
                    break
            if not os.path.isdir(path):
                os.mkdir(path) 
    
    #todo: elif ISMAC: or use linux/unix?
    else:
        paths = ['/tmp', '/var/tmp']
        if preserved:
            paths = reversed(paths)
        for path in paths:
            if os.path.isdir(path):
                break
        else:
            raise RuntimeError('Could not locate temporary directory.')
    
    # Get path specific for this app
    if appname:
        path = os.path.join(path, appname)
        # Make sure it exists
        if not os.path.isdir(path):
            os.mkdir(path)
    
    # Done
    return _test_if_dir_exists(path, 'temp')


def user_dir():
    """ user_dir()
    
    Get the path to the user directory. (e.g. "/home/jack", "c:/Users/jack")
    
    """
    path = os.path.expanduser('~')
    return _test_if_dir_exists(path, 'user')


def appdata_dir(appname=None, roaming=False):
    """ appdata_dir(appname=None, roaming=False)
    
    Get the path to the application directory, where applications are allowed
    to write user specific files (e.g. configurations). For non-user specific
    data, consider using common_appdata_dir().
    
    If appname is given, a subdir is appended (and created if necessary). 
    
    If roaming is True, will prefer a roaming directory (Windows Vista/7).
    
    """
    
    # Define default user directory
    userDir = os.path.expanduser('~')
    
    # Get system app data dir
    if ISWIN:
        if roaming:
            path = _path_from_environ('APPDATA')
        else:
            path = _path_from_environ('LOCALAPPDATA', 'APPDATA') # Prefer local
        if not (path and os.path.isdir(path)):
            path = userDir
    else: # Linux and others
        path = userDir
    
    # todo: moet onder Mac nou in ~/Libraries/appname of ~/.appname
    
    # Get path specific for this app
    if appname:
        if not ISWIN:
            appname = '.' + appname
        path = os.path.join(path, appname)
        # Make sure it exists
        if not os.path.isdir(path):
            os.mkdir(path)
    
    # Done
    return _test_if_dir_exists(path, 'appdata')


def common_appdata_dir(appname=None):
    """ common_appdata_dir(appname=None)
    
    Get the path to the common application directory. Applications are
    allowed to write files here. For user specific data, consider using 
    appdata_dir().
    
    If appname is given, a subdir is appended (and created if necessary). 
    
    """
    
    # Init
    path = None
    
    # Try to get path 
    if ISWIN:
        path = _path_from_environ('ALLUSERSPROFILE', 'PROGRAMDATA')
    elif ISMAC:
        # todo: ok onder Mac?
        path = os.path.join(user_dir(), 'Libraries')
    else:
        # Not sure what to use. Apps are only allowed to write to the home
        # dir and tmp dir, right?
        pass
    
    # If no success, use appdata_dir() instead
    if not (path and os.path.isdir(path)):
        path = appdata_dir()
    
    # Get path specific for this app
    if appname:
        path = os.path.join(path, appname)
        # Make sure it exists
        if not os.path.isdir(path):
            os.mkdir(path)
    
    # Done
    return _test_if_dir_exists(path, 'common_appdata')


#  Other approaches that we considered, but which did not work for links,
#  or are less reliable for other reasons are:
#      * sys.executable: does not work for links
#      * sys.prefix: dito
#      * sys.exec_prefix: dito
#      * os.__file__: does not work when frozen
#      * __file__: only accessable from main module namespace, does not work when frozen 

# todo: get this included in Python sys or os module!
def application_dir():
    """ application_dir()
    
    Get the directory in which the current application is located. 
    The "application" can be a Python script or a frozen application. 
    
    This function raises a RuntimeError if in interpreter mode.
    
    """
    isfrozen = getattr(sys, 'frozen', None)
    # Test if the current process can be considered an "application"
    if not sys.path or not sys.path[0]:
        raise RuntimeError('Cannot determine app path because sys.path[0] is empty!')
    # Get the path. If frozen, sys.path[0] is the name of the executable,
    # otherwise it is the path to the directory that contains the script.
    thepath = sys.path[0]
    if isfrozen:
        thepath = os.path.dirname(thepath)
    # Return absolute version, or symlinks may not work
    return os.path.abspath(thepath)


# todo: use this in IEP    
# todo: for IEP: make sure it's on sys.path[0]. Set to /source if frozen


## Pyzo specific
# todo: NOTE this part is under development

def assert_pyzo_dir(**kwargs):
    """ assert_pyzo_dir()
    
    Check if there is a Pyzo dir. Raises an error if the is no Pyzo dir or
    if this is a frozen application.
    
    """
    if pyzo_dir(**kwargs) is None:
        raise AssertionError('There is no Pyzo dir.')


def pyzo_dir(**kwargs):
    """ pyzo_dir()
    
    Get the location of the Pyzo directory. Returns None if there is no Pyzo
    directory registered. For frozen applications, this returns None, unless
    the keyword arg 'ignore_frozen' is given and True.
    
    The registration is performed by putting a text file called pyzo_path.txt
    in appdata_dir('pyzo') which contains the path name.
    
    """
    
    # If frozen, we don't have (or do not acknowledge) a Pyzo dir
    ignore_frozen = 'ignore_frozen' in kwargs and kwargs['ignore_frozen']
    if is_frozen() and not ignore_frozen:
        return None
    
    # Get dir, not roaming
    appdataDir = appdata_dir('pyzo')
    
    # Read file 
    configFile = os.path.join(appdataDir, 'pyzo_path.txt')
    if os.path.isfile(configFile):
        path = open(configFile, 'rb').read().decode('utf-8').strip()
        if not os.path.isdir(path):
            raise RuntimeError('Registered Pyzo directory doed not exist.')
    else:
        path = None
    
    # We could try and find it in c:/pyzo and /home/pyzo etc.
    # Which would make it work in many cases, but then we would not detect
    # an error of registering the pyzo path
    
    return path


def _pyzo_sub_dir(sub, appname=None, **kwargs):
    """ get pyzo subdir. """
    
    # Get pyzo dir
    path = pyzo_dir(**kwargs)
    if path is None:
        return None
    
    # Get sub dir
    path = os.path.join(path, sub)
    if not os.path.isdir(path):
        os.mkdir(path)
    
    # Get path specific for this app
    if appname:
        path = os.path.join(path, appname)
        # Make sure it exists
        if not os.path.isdir(path):
            os.mkdir(path)
    
    return path


def pyzo_package_dir(**kwargs):
    """ pyzo_package_dir()
    
    Get the path to the directory where Pyzo installs the Python packages.
    
    Returns None if there is no Pyzo directory registered.
    
    """
    # Get pyzo dir
    path = pyzo_dir(**kwargs)
    if path is None:
        return None
    
    # Get sub dir
    path = os.path.join(path, 'packages')
    if not os.path.isdir(path):
        os.mkdir(path)
    
    return path


def pyzo_lib_dir(**kwargs):
    """ pyzo_lib_dir()
    
    Get the path to the directory where Pyzo stores a few dynamic libraries.
    
    Returns None if there is no Pyzo directory registered.
    
    """
    # Get pyzo dir
    path = pyzo_dir(**kwargs)
    if path is None:
        return None
    
    # Get number of bits of this process
    NBITS = 8 * struct.calcsize("P")
    sub = "lib%i" % NBITS
    
    # Get sub dir
    path = os.path.join(path, sub)
    if not os.path.isdir(path):
        os.mkdir(path)
    
    return path



## Windows specific

# Maybe for directory of programs, pictures etc.
