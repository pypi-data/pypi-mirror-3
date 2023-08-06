from setuptools import setup, find_packages

import sys
sys.path.insert(0, 'src')

from rosci import __version__

setup(name='rosci',
      version= __version__,
      packages=['rosci', 'rosci_templates'],
      package_dir = {'rosci':'src/rosci',
                     'rosci_templates': 'templates'},
      package_data = {'rosci_templates': ['*.xml']},
      install_requires=['rosdep'],
      scripts = [
        'scripts/rosci',
        'scripts/rosci-catkin-depends',
        'scripts/rosci-clean-junit-xml',
        ],
      author = "Ken Conley", 
      author_email = "kwc@willowgarage.com",
      url = "http://www.ros.org/wiki/rosci",
      download_url = "http://pr.willowgarage.com/downloads/rosci/", 
      keywords = ["ROS"],
      classifiers = [
        "Programming Language :: Python", 
        "License :: OSI Approved :: BSD License" ],
      description = "rosci continuous integration tool", 
      long_description = """\
Command-line tool for setting up CI jobs on jenkins.
""",
      license = "BSD"
      )
