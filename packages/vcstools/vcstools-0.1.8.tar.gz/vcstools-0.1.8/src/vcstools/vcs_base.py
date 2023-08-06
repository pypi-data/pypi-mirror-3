# Software License Agreement (BSD License)
#
# Copyright (c) 2010, Willow Garage, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Willow Garage, Inc. nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
"""
vcs support library base class.
"""
import os
import shlex

class VcsError(Exception):
    """To be thrown when an SCM Client faces a situation because of a
    violated assumption"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


def normalized_rel_path(path, basepath):
    """
    Utility function for subclasses.
    
    If path is absolute, return relative path to it from
    basepath. If relative, return it normalized.
    
    :param path: an absolute or relative path
    :param basepath: if path is absolute, shall be made relative to this
    :returns: a normalized relative path
    """
    # gracefully ignore invalid input absolute path + no basepath
    if path is None:
        return basepath
    if os.path.isabs(path) and basepath is not None:
        return os.path.normpath(os.path.relpath(os.path.realpath(path), os.path.realpath(basepath)))
    return os.path.normpath(path)

def sanitized(arg):
    if arg is None or arg.strip() == '':
        return ''
    safe_arg = '\"%s\"'%arg
    if len(shlex.split(safe_arg)) != 1:
        raise VcsError("Shell injection attempt detected: %s"%arg)
    return safe_arg


class VcsClientBase:

    
    def __init__(self, vcs_type_name, path):
        """
        subclasses may raise VcsError when a dependency is missing
        """
        self._path = path
        self._vcs_type_name = vcs_type_name

    @staticmethod
    def get_environment_metadata():
        """
        For debugging purposes, returns a dict containing information
        about the environment, like the version of the SCM client, or
        version of libraries involved.
        Suggest considering keywords "version", "dependency", "features" first.
        :returns: a dict containing relevant information
        :rtype: dict
        """
        raise NotImplementedError("Base class get_environment_metadata method must be overridden")
    
    def path_exists(self):
        return os.path.exists(self._path)
        
    def get_path(self):
        return self._path

    def get_url(self):
        """
        :returns: The source control url for the path
        :rtype: str
        """
        raise NotImplementedError("Base class get_url method must be overridden")

    def get_version(self, spec=None):
        """
        Find an identifier for a the current or a specified
        revision. Token spec might be a tagname, branchname,
        version-id, SHA-ID, ... depending on the VCS implementation.

        :param spec: token for identifying repository revision
        :type spec: str
        :returns: current revision number of the repository.  Or if
        spec is provided, the respective revision number.
        :rtype: str
        """
        raise NotImplementedError, "Base class get_version method must be overridden"

    def checkout(self, url, version):
        """
        Attempts to create a local repository given a remote
        url. Fails if a direcotry exists already in target
        location. If a spec is provided, the local repository
        will be updated to that revision. It is possible that
        after a failed call to checkout, a repository still exists,
        e.g. if an invalid revision spec was given.

        :param spec: token for identifying repository revision
        :type spec: str
        :returns: True if successful
        """
        raise NotImplementedError("Base class checkout method must be overridden")

    def update(self, spec):
        """
        Sets the local copy of the repository to a version matching
        the spec. Fails when there are uncommited changes.
        On failures (also e.g. network failure) grants the
        checked out files are in the same state as before the call.
        :param spec: token for identifying repository revision
        desired.  Token might be a tagname, branchname, version-id, 
        SHA-ID, ... depending on the VCS implementation.
        :return True on success, False else
        """
        raise NotImplementedError("Base class update method must be overridden")

    def detect_presence(self):
        """For auto detection"""
        raise NotImplementedError("Base class detect_presence method must be overridden")

    def get_vcs_type_name(self):
        """ used when auto detected """
        return self._vcs_type_name

    def get_diff(self, basepath=None):
        """
        :param basepath: diff paths will be relative to this, if any
        :returns: A string showing local differences
        :rtype: str
        """
        raise NotImplementedError("Base class get_diff method must be overridden")

    def get_status(self, basepath=None, untracked=False):
        """
        Calls scm status command. semantics of untracked are difficult
        to generalize. In SVN, this would be new files only. In git,
        hg, bzr, this would be changesthat have not been added for
        commit.

        :param basepath: status path will be relative to this, if any
        :param untracked: whether to also show changes that would not commit
        :returns: A string summarizing locally modified files
        :rtype: str
        """
        raise NotImplementedError("Base class get_status method must be overridden")

