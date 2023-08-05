from distutils.core import setup

import adu

setup(name='python-adu',
      version=adu.__version__,
      description='python wrapper around Team Approach ADU format',
      author='Jacob Smullyan',
      author_email='jsmullyan@gmail.com',
      url='http://bitbucket.org/smulloni/python-adu/',
      packages=['adu'],
      package_data={'adu': ['*.txt']},
      license='MIT',
     )
