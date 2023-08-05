from setuptools import setup
setup(name='fastVAR',
      version='1.0',
      description='Vector AutoRegressive model for time series data.  Requires numpy.',
      author='Jeffrey Wong',
      author_email='jeff.ct.wong@stanford.edu',
      url='http://www.stanford.edu/~jeffwong',
      py_modules=['fastVAR'],
      install_requires=['LargeRegression > 1.0'],
      )
