from setuptools import setup


long_desc = open('README.rst', 'r').read()

setup(name='pytest_gae',
      version='0.2.2',
      description="pytest plugin for apps written with Google's AppEngine",
      long_description=long_desc,
      author='Petras Zdanavicius (petraszd)',
      author_email='petraszd@gmail.com',
      url='http://bitbucket.org/petraszd/pytest_gae/',
      py_modules=['pytest_gae'],
      requires=['pytest'],
      entry_points={'pytest11': ['pytest_gae = pytest_gae']},
      license='MIT License',
      keywords='py.test pytest google app engine',
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 2',
                   'Topic :: Software Development :: Testing'])
