from setuptools import setup

try:
    import carton
    description = carton.__doc__
except ImportError:
    description = None

version = '0.2.3'

setup(name='carton',
      version=version,
      description="make self-extracting virtualenvs",
      long_description=description,
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='mozilla',
      author='Jeff Hammel',
      author_email='jhammel@mozilla.com',
      url='http://k0s.org/mozilla/hg/carton',
      license='MPL',
      py_modules=['carton'],
      packages=[],
      include_package_data=True,
      zip_safe=False,
      install_requires=[],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      carton = carton:main
      """,
      )
