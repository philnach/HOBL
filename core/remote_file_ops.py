#!/usr/bin/env python

from builtins import str
from builtins import *
import os
import os.path
import shutil
import sys
import win32wnet
#import exceptions
import builtins as exceptions

import time

def net_copy(host, source, dest_dir, username=None, password=None, move=False):
    """ Copies files or directories to a remote computer. """
    wnet_connect(host, username, password)
    dest_dir = convert_unc(host, dest_dir)

    # Pad a backslash to the destination directory if not provided.
    if not dest_dir[len(dest_dir) - 1] == '\\':
        dest_dir = ''.join([dest_dir, '\\'])

    # Create the destination dir if its not there.
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    else:
        # Create a directory anyway if file exists so as to raise an error.
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)

    if move:
        shutil.move(source, dest_dir)
    else:
        shutil.copy(source, dest_dir)

def net_copy_file(host, source, dest, username=None, password=None, move=False):
    """ Copies files or directories to a remote computer. """
    wnet_connect(host, username, password)
    dest = convert_unc(host, dest)

    shutil.copyfile(source, dest)

def net_copy_back(host, source, dest_dir, username=None, password=None):
    """ Copies files back from a remote computer. """
    wnet_connect(host, username, password)
    source = convert_unc(host, source)

    # Create the destination dir if its not there.
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    else:
        # Create a directory anyway if file exists so as to raise an error.
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)
            
    shutil.copy(source, dest_dir)

# Includes the top level dir
def net_copy_tree(host, src, dst, username=None, password=None, symlinks=False, ignore=None, connected=False):
    """ Recursively copies directory tree from a remote computer. """
    if not connected:
        wnet_connect(host, username, password)
        dst = convert_unc(host, dst)

    names = os.listdir(src)
   
    # print "NAMES: ", names
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    # print "Checking ", dst
    if not os.path.exists(dst):
        os.makedirs(dst)

    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        # print "working on ", srcname, dstname
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                net_copy_tree(host, srcname, dstname, symlinks, ignore, connected=True)
            else:
                shutil.copy2(srcname, dstname)
            # XXX What about devices, sockets etc.?
        except (IOError, os.error) as why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except shutil.Error as err:
            errors.extend(err.args[0])
    try:
        shutil.copystat(src, dst)
    except WindowsError:
        # can't copy file access times on Windows
        pass
    except OSError as why:
        errors.extend((src, dst, str(why)))
    if errors:
        raise shutil.Error(errors)

# Does not include the top level dir
def net_copy_tree_back(host, src, dst, username=None, password=None, symlinks=False, ignore=None, connected=False):
    """ Recursively copies directory tree from a remote computer. """
    if not connected:
        wnet_connect(host, username, password)
        src = convert_unc(host, src)

    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    if not os.path.exists(dst):
        os.makedirs(dst)

    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                net_copy_tree_back(host, srcname, dstname, symlinks, ignore, connected=True)
            else:
                shutil.copy2(srcname, dstname)
            # XXX What about devices, sockets etc.?
        except (IOError, os.error) as why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except shutil.Error as err:
            errors.extend(err.args[0])
    try:
        shutil.copystat(src, dst)
    except WindowsError:
        # can't copy file access times on Windows
        pass
    except OSError as why:
        errors.extend((src, dst, str(why)))
    if errors:
        raise shutil.Error(errors)

def net_delete(host, path, username=None, password=None):
    """ Deletes files or directories on a remote computer. """

    wnet_connect(host, username, password)

    path = convert_unc(host, path)
    if os.path.exists(path):
        # Delete directory tree if object is a directory.
        if os.path.isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path)
    else:
        # Remove anyway if non-existent so as to raise an error.
        os.remove(path)

def net_make_dir(host, path, username=None, password=None, delete=False):
    """ Deletes files or directories on a remote computer. """

    wnet_connect(host, username, password)

    path = convert_unc(host, path)
    if os.path.exists(path):
        if delete:
            shutil.rmtree(path)
            # Create directory
            os.mkdir(path)
    else:
        # Create directory
        os.mkdir(path)

def net_move(host, source, dest_dir, username=None, password=None):
    return netcopy(host, source, dest_dir, username, password, True)

def convert_unc(host, path):
    """ Convert a file path on a host to a UNC path."""
    return ''.join(['\\\\', host, '\\', path.replace(':', '$')])

def wnet_connect(host, username, password):
    if "http" in host or '\\\\' in host:
        unc = host
    else:
        unc = ''.join(['\\\\', host])

    try:
        win32wnet.WNetAddConnection2(0, None, unc, None, username, password)
    except Exception as err:
        if isinstance(err, win32wnet.error):
            # Disconnect previous connections if detected, and reconnect.
            if err[0] == 1219:
                win32wnet.WNetCancelConnection2(unc, 0, 0)
                return wnet_connect(host, username, password)
        raise err

