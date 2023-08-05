from distutils.core import setup

with open("README.rst") as fh:
        long_description = fh.read()

setup(name = 'simplelog',
      version = '0.2',              
      description = 'Simple interface for logging in python',
      author = 'Kevin S Lin',
      author_email = 'kevinslin8@gmail.com',
      url = 'kevinslin.com',
      long_description = long_description,
      packages = ['simplelog']
      )   

      
