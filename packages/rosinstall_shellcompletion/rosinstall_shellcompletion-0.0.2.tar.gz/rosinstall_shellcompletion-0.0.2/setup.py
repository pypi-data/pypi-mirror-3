from setuptools import setup

    
setup(name='rosinstall_shellcompletion',
      version= '0.0.2',
      install_requires = ['rosinstall'],
      data_files=[('/etc/bash_completion.d', ['contrib/rosws.bash',
                                              'contrib/rosinstall.bash'])],
      author = "Tully Foote", 
      author_email = "tfoote@willowgarage.com",
      url = "http://www.ros.org/wiki/rosinstall",
      keywords = [],
      classifiers = [
        "Programming Language :: Unix Shell", 
        "License :: OSI Approved :: BSD License" ],
      description = "Linux shell completion for rosinstall commands", 
      long_description = """\
Linux shell completion for rosinstall commands
Wont work using easy_install, use pip. Only supports bash for now.
""",
      license = "BSD"
      )
