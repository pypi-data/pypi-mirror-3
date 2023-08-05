from setuptools import setup, find_packages

#must be called dropbox-client so it overwrites the older dropbox SDK
setup(name='dropbox',
      version='1.1',
      description='Dropbox REST API Client',
      author='Dropbox, Inc.',
      author_email='support-api@dropbox.com',
      url='http://www.dropbox.com/',
      packages=['dropbox'],
      install_requires = ['oauth', 'simplejson'],
     )

