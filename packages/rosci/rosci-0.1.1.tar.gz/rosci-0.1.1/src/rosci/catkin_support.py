import os
import sys
import yaml

from .rosdep_support import resolve_rosdeps

def catkin_depends_to_apt(stack_yaml_file, rosdistro_name, os_name, os_platform):
    with open(stack_yaml_file) as f:
        stack_data = yaml.load(f.read())
    rosdep_keys = stack_data['Depends']
    if type(rosdep_keys) == str:
        rosdep_keys = list(set([x.strip() for x in rosdep_keys.split(',') if len(x.strip()) > 0]))
    return resolve_rosdeps(rosdep_keys, rosdistro_name, os_name, os_platform)

