from distutils.core import setup

setup(name="Pwmngr",
      version="0.1dev",
      author="Florent D'halluin",
      author_email="flal@melix.net",
      url="https://bitbucket.org/flal/pwmngr",
      packages=["pwmngr"],
      scripts=['bin/pwmngr'],
      license="Beerware",
      description="a CLI password manager",
      long_description=open('README.txt').read(),
      install_requires=[
        "pycrypto >= 2.4",
        ],
      )
      
