from setuptools import setup, find_packages

setup(name = "OSR",
      version = "0.0.1",
      description = "Automated DJ/Announcer",
      author = "Julian K. Arni",
      license = "EPL",
      author_email = "jkarni@gmail.com",
      packages = find_packages(),
      install_requires = ["Pyglet == 1.1.4",
      "eyeD3 >=0.6.18"],
      setup_requires = ["Pyglet == 1.1.4",
      "eyeD3 >=0.6.18"],
      )