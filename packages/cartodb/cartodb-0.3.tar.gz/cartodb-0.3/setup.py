
from distutils.core import setup
import sys

REQUIRES = ['oauth2']
if sys.version_info < (2 , 6):
    REQUIRES.append('simplejson')

setup(name='cartodb', 
      author = 'Javi Santana', 
      author_email = 'jsantana@vizzuality.com',
      description = 'client to access cartodb api',
      url='https://github.com/javisantana/cartodb',
      version='0.3',
      install_requires=REQUIRES,
      packages=['cartodb'],
      requires = REQUIRES
)
