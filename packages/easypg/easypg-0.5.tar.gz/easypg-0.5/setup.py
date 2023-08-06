# easypg setup
# (NDE, 2012-02-17)

from distutils.core import setup

setup(
  name='easypg',
  version='0.5',
  description='Various tools to simplify the use of Pygame',
  long_description=open('README').read(),
  author='Nick Efford',
  author_email='nick.efford@gmail.com',
  url='http://bitbucket.org/pythoneer/easypg',
  packages=['easypg'],
  platforms='any',
  license='MIT',
  classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: Education',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.2',
    'Topic :: Games/Entertainment',
    'Topic :: Multimedia :: Graphics',
    'Topic :: Software Development :: Libraries :: pygame',
    'Topic :: Software Development :: Libraries :: Python Modules',
  ],
)
