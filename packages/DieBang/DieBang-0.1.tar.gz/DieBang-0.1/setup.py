from setuptools import setup

readme = open('README.txt').read()
setup(name='DieBang',
      version='0.1',
      author='Philip Schleihauf',
      author_email='uniphil@gmail.com',
      license='GPLv3',
      description='Remove inline comments denoted by \'!\' from files',
      long_description=readme,
      py_modules=['diebang'])
