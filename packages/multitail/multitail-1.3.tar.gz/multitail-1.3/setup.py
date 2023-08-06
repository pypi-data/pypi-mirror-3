from setuptools import setup


import os.path
here = os.path.dirname(os.path.abspath(__file__))


setup(
  name = 'multitail',
  version = '1.3',
  author = 'Sergey Kirilov',
  author_email = 'sergey.kirillov@gmail.com',
  url='https://bitbucket.org/rushman/multitail', 
  install_requires=[],
  license="Apache License 2.0",   
  keywords="tail",
  description='Python generator which implements `tail -f`-like behaviour, with support for tailing multiple files.',
  long_description=open(os.path.join(here, 'README.rst')).read().decode('utf-8'),
  py_modules=['multitail']
)
