from distutils.core import setup

setup(name='python-adu',
      version='0.2',
      description='python wrapper around Team Approach ADU format',
      author='Jacob Smullyan',
      author_email='jsmullyan@gmail.com',
      url='http://bitbucket.org/smulloni/python-adu/',
      packages=['adu'],
      package_data={'adu': ['*.txt']},
      license='MIT',
     )
