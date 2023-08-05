from distutils.core import setup

setup(name='rospkg',
      version= '0.2.3',
      packages=['rospkg'],
      package_dir = {'':'src'},
      scripts = [],
      author = "Ken Conley", 
      author_email = "kwc@willowgarage.com",
      url = "http://www.ros.org/wiki/rospkg",
      download_url = "http://pr.willowgarage.com/downloads/rospkg/", 
      keywords = ["ROS"],
      classifiers = [
        "Programming Language :: Python", 
        "License :: OSI Approved :: BSD License" ],
      description = "ROS package library", 
      long_description = """\
Library for retrieving information about ROS packages and stacks.
""",
      license = "BSD"
      )
