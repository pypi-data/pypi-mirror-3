# Software License Agreement (BSD License)
#
# Copyright (c) 2012, Willow Garage, Inc.
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

import os
import jenkins
import pkg_resources
import sys
import yaml

from .ci_base import InvalidCiConfig, get_default_rosci_config_dir, TEMPLATES_PKG

class JenkinsConfig(object):

    def __init__(self, url, username=None, password=None):
        """
        :raises: :exc:`InvalidCiConfig`
        """
        self.url = url
        self.username = username
        self.password = password
        
        if username is None:
            raise InvalidCiConfig("no jenkins username configured; cannot create CI jobs")
        if password is None:
            raise InvalidCiConfig("no jenkins password configured; cannot create CI jobs")

def JenkinsConfig_to_handle(server_config):
    return jenkins.Jenkins(server_config.url, server_config.username, server_config.password)

def get_default_server_config_file():
    rosci_dir = get_default_rosci_config_dir()
    return os.path.join(rosci_dir, 'server.yaml')
    
def load_server_config_file(server_config_file):
    """
    :raises: :exc:`InvalidCiConfig`
    :returns: :class:`JenkinsConfig` instance
    """
    #TODO: typed exception
    if not os.path.isfile(server_config_file):
        raise RuntimeException("server config file [%s] does not exist"%(server_config_file))

    with open(server_config_file) as f:
        server = yaml.load(f.read())
    if server['type'] != 'jenkins':
        raise InvalidCiConfig("unknown CI server type: %s"%(server['type']))
    return JenkinsConfig(server['url'], server['username'], server['password'])

def get_scm_template_fragment(vcs_type):
    template_name = 'scm-%s-fragment.xml'%(vcs_type)
    if not pkg_resources.resource_exists(TEMPLATES_PKG, template_name):
        raise RuntimeError("cannot locate template fragment: %s"%(template_name))
    
    f = pkg_resources.resource_stream(TEMPLATES_PKG, template_name)
    return f.read()

def VcsConfig_to_scm_fragment(vcs_config, local_name, branch='devel'):
    # have to set local_name, source, and version variables
    uri, version = vcs_config.get_branch(branch, anonymous=True)
    vcs_type = vcs_config.type
    source = uri
    
    if vcs_type == 'hg':
        version = version or 'default'
    elif vcs_type == 'svn':
        if version is not None:
            source = "%s@%s"%(uri, version)
    elif vcs_type == 'git':
        version = version or 'master'
    return get_scm_template_fragment(vcs_type)%locals()
