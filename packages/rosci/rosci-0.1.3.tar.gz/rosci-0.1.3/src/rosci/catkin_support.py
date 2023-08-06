import rospkg.stack

from .rosdep_support import resolve_rosdeps

def catkin_depends_to_apt(stack_xml_file, rosdistro_name, os_name, os_platform):
    stack = rospkg.stack.parse_stack_file(stack_xml_file)
    rosdep_keys = [d.name for d in stack.depends]
    return resolve_rosdeps(rosdep_keys, rosdistro_name, os_name, os_platform)
